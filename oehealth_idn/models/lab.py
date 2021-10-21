from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
import requests, json, datetime
from datetime import timedelta
import pytz
import logging

_logger = logging.getLogger(__name__)


class OehMedicalLabTest(models.Model):
    _inherit = "oeh.medical.lab.test"
    
    PAYMENT_TYPE = [
        ('Personal', 'Personal'),
        ('Corporate', 'Corporate'),
        ('Insurance', 'Insurance'),
        ('Employee', 'Employee')
    ]

    LABTEST_STATE = [
     ('Draft', 'Draft'),
     ('Test In Progress', 'Test In Progress'),
     ('Completed', 'Completed'),
     ('Invoiced', 'Invoiced'), ('Cancelled', 'Cancelled')]

    @api.one
    def cancelled_lab(self):
        self.state = "Cancelled"

    @api.multi
    def create_sale(self):
        obj = self.env['sale.order']
        line_obj = self.env['sale.order.line']
        inv_ids = []
        guarantor = 0
        arrival = 0
        for acc in self:
            if acc.payment != 'Personal' AND acc.state not in ['Draft', 'Test In Progress']:
                if acc.patient:
                    if acc.payment == 'Insurance':
                        guarantor = acc.insurance.ins_type.partner_id.id
                    elif acc.payment == 'Corporate':
                        guarantor = acc.company.id
                    elif acc.payment == 'Employee':
                        guarantor = acc.employee_id.current_insurance.ins_type.partner_id.id
                    else:
                        guarantor = acc.patient.partner_id.id
                        #guarantor = acc.company.id

                    unit_registration_id = self.env['unit.registration'].search([('arrival_id', '=', acc.walkin.id)])

                    val_obj = {'reg_id': unit_registration_id.id, 
                    'arrival_id': acc.lab_test_walkin_id.id,
                    'labtest_id': acc.id,
                    'patient_id': acc.patient.id, 
                    'doctor_id': acc.requestor.id, 
                    'partner_id': acc.patient.partner_id.id, 
                    'partner_invoice_id': guarantor, 
                    'partner_shipping_id': acc.patient.partner_id.id, 
                    'pricelist_id': acc.patient.partner_id.property_product_pricelist.id, 
                    'location_id': self.env['stock.location'].search([('unit_ids.operating_id', '=', self.env.user.default_operating_unit_id.id)], limit=1).id, 
                    #'operating_unit_id': acc.unit.operating_id.id or False
                    }
                    inv_ids = obj.create(val_obj)
                    
                    if inv_ids:
                        inv_id = inv_ids.id
                        if self.lab_test_walkin_id and not self.lab_test_walkin_id.have_register:
                            product = self.env['product.product'].search([('auto_billing', '!=', False)])
                            for p in product:
                                vals = {
                                    'order_id': inv_id, 
                                    'product_id': p.id, 
                                    'name': p.name, 
                                    'product_uom_qty': 1, 
                                    'product_uom': p.uom_id.id, 
                                    'price_unit': p.lst_price, 
                                    'doctor_id': False
                                }
                                line_obj.create(vals)
                            arrival = self.env['oeh.medical.appointment.register.walkin'].browse(self.lab_test_walkin_id.id)
                            arrival.write({'have_register': True})
                else:
                    raise UserError(_('Configuration error! \n Could not find any patient to create the transactions !'))
            else:
                raise UserError(_('Can not create transaction because ... !'))

        return {
            'name': 'Transactions', 
            'view_type': 'form', 
            'view_mode': 'form', 
            'res_id': inv_id, 
            'res_model': 'sale.order', 
            'type': 'ir.actions.act_window'
        }

    lab_test_walkin_id = fields.Many2one(comodel_name='oeh.medical.appointment.register.walkin', string='Lab Test Walkin')
    payment = fields.Selection(PAYMENT_TYPE, string='Payment Guarantor', default='Personal', readonly=True, states={'Draft': [('readonly', False)]}, track_visibility='onchange')
    company = fields.Many2one(comodel_name='res.partner', string='Company', readonly=True, states={'Draft': [('readonly', False)]}, track_visibility='onchange')
    insurance = fields.Many2one(comodel_name='medical.insurance', string='Insurance', readonly=True, states={'Draft': [('readonly', False)]}, track_visibility='onchange')
    employee_id = fields.Many2one('oeh.medical.patient', 'Employee', readonly=True)
    payment_guarantor_discount_id = fields.Many2one('payment.guarantor.discount', 'Payment Guarantor Discount')
    state = fields.Selection(LABTEST_STATE, string='State', readonly=True, default=lambda *a: 'Draft')
  
   