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
     ('Invoiced', 'Invoiced'), ('Cancelled', 'Cancelled'), ('Unlock', 'Unlock'),
     ('Lock', 'Lock')]

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
            #if acc.payment != 'Personal' and acc.state not in ['Draft', 'Test In Progress']:
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
                _logger.info(self.env.user.default_operating_unit_id)
                _logger.info("Get User Warehouse")
                warehouse_id = self.env['stock.warehouse'].search([('operating_unit_id','=',self.env.user.default_operating_unit_id.id)], limit=1)
            
                val_obj = {
                    #'reg_id': acc.id, 
                    'arrival_id': acc.walkin.id, 
                    'patient_id': acc.patient.id, 
                    'doctor_id': acc.requestor.id, 
                    'partner_id': acc.patient.partner_id.id, 
                    'partner_invoice_id': guarantor, 
                    'partner_shipping_id': acc.patient.partner_id.id, 
                    'payment_guarantor_discount_id': acc.payment_guarantor_discount_id.id, 
                    'pricelist_id': acc.patient.partner_id.property_product_pricelist.id, 
                    'location_id':  self.env['stock.location'].search([('unit_ids', 'in', (self.env.user.default_unit_administration_id.id))], limit=1).id,
                    #'operating_unit_id': acc.operating_unit_id.id or False,
                    'operating_unit_id': self.env.user.default_operating_unit_id.id,
                    'warehouse_id':  False if not warehouse_id else warehouse_id.id

                }
                inv_ids = obj.create(val_obj)
                
                if inv_ids:
                    inv_id = inv_ids.id

                    discount = 0.0
                    product_id = self.env['product.product'].browse(36527)
                    if acc.payment_guarantor_discount_id:
                        if product_id.item_type == 'General Item':
                            discount = acc.payment_guarantor_discount_id.general_item
                        elif product_id.item_type == 'Medical Item':        
                            discount = acc.payment_guarantor_discount_id.medical_item
                        elif product_id.item_type == 'Food Item':        
                            discount = acc.payment_guarantor_discount_id.food_item
                        elif product_id.item_type == 'Medicine':        
                            discount = acc.payment_guarantor_discount_id.medicine
                        elif product_id.item_type == 'Doctor':        
                            discount = acc.payment_guarantor_discount_id.doctor
                        elif product_id.item_type == 'Nurse':        
                            discount = acc.payment_guarantor_discount_id.nurse
                    vals = {
                        'order_id': inv_id, 
                        'product_id': 36527, 
                        'name': acc.test_type.name, 
                        'prescribe_qty': 1, 
                        'product_uom_qty': 1, 
                        'discount_type': 'percent',
                        'discount': discount,
                        #product_uom': ps.name.uom_id.id, 
                        'price_unit': acc.test_type.test_charge
                    }
                    line_obj.create(vals)
                
                self.write(
                    {
                        'state': 'Invoiced',
                        'sale_order_id': inv_id
                    }
                )
                inv_ids.action_confirm()
            else:
                raise UserError(_('Can not create the transactions because Payment Guarantor is Personal !'))
            return {
                'name': 'Transactions', 
                'view_type': 'form', 
                'view_mode': 'form', 
                'res_id': inv_id, 
                'res_model': 'sale.order', 
                'type': 'ir.actions.act_window'
            }

    def action_next(self):
        if self.queue_trans_id.type_id.unit_administration_id.id == self.env.user.default_unit_administration_id.id:
            next_type_id = self.queue_trans_id.type_id.next_type_id
            self.queue_trans_id.write({'type_id' : next_type_id.id, 'state': 'draft'})        
            self.state = 'Unlock'
        else:
            raise Warning('Queue have different unit administration')

    def get_user_unit_administration(self):
        for row in self:
            _logger.info(self.env.user.default_unit_administration_id.id)
            row.user_unit_administration_id = self.env.user.default_unit_administration_id.id
    
    lab_test_walkin_id = fields.Many2one(comodel_name='oeh.medical.appointment.register.walkin', string='Lab Test Walkin')
    payment = fields.Selection(PAYMENT_TYPE, string='Payment Guarantor', default='Personal', readonly=True, states={'Draft': [('readonly', False)]}, track_visibility='onchange')
    company = fields.Many2one(comodel_name='res.partner', string='Company', readonly=True, states={'Draft': [('readonly', False)]}, track_visibility='onchange')
    insurance = fields.Many2one(comodel_name='medical.insurance', string='Insurance', readonly=True, states={'Draft': [('readonly', False)]}, track_visibility='onchange')
    employee_id = fields.Many2one('oeh.medical.patient', 'Employee', readonly=True)
    payment_guarantor_discount_id = fields.Many2one('payment.guarantor.discount', 'Payment Guarantor Discount')
    state = fields.Selection(LABTEST_STATE, string='State', readonly=True, default=lambda *a: 'Draft')
    sale_order_id = fields.Many2one('sale.order', string='Order#', readonly=True)
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', default=lambda self: self.env.user.default_operating_unit_id.id)

    queue_trans_id = fields.Many2one('queue.trans','Queue', domain=[('unit','','')])
    type_id = fields.Many2one('queue.type', related="queue_trans_id.type_id", readonly=True)
    user_unit_administration_id = fields.Many2one('unit.administration', compute="get_user_unit_administration")
    is_on_unit_administration = fields.Boolean('', compute="get_user_unit_administration")


    def set_lock(self):
        self.write({'state': 'Lock'})

    def set_unlock(self):
        self.write({'state': 'Unlock'})

    @api.model
    def create(self, vals):
        res = super(OehMedicalLabTest, self).create(vals)
        if res.payment == 'Personal':
            #Personal
            domain = [
                ('payment','=', 'Personal')
            ]
            payment_quarantor_discount_id = self.env['payment.guarantor.discount'].search(domain, limit=1)
            if not payment_quarantor_discount_id:
                raise Warning(_('Payment Guarantor Discount not found'))
            res.payment_quarantor_discount_id = payment_quarantor_discount_id
        elif res.payment == 'Corporate':
            #Corporate
            _logger.info('Corporate')
            domain = [
                ('payment','=', 'Corporate'),
                ('company','=', res.company.id)
            ]
            _logger.info(domain)
            payment_guarantor_discount_id = self.env['payment.guarantor.discount'].search(domain, limit=1)
            if not payment_guarantor_discount_id:
                raise Warning(_('Payment Guarantor Discount not found'))
            _logger.info(payment_guarantor_discount_id.description)
            res.payment_guarantor_discount_id = payment_guarantor_discount_id.id
        elif res.payment == 'Insurance':
            #Insurance
            _logger.info('Insurance')
            domain = [
                ('payment','=', 'Insurance'),
                ('insurance_type_id','=', res.insurance.ins_type.id)
            ]
            _logger.info(domain)
            payment_guarantor_discount_id = self.env['payment.guarantor.discount'].search(domain, limit=1)
            if not payment_guarantor_discount_id:
                raise Warning(_('Payment Guarantor Discount not found'))
            _logger.info(payment_guarantor_discount_id.description)
            res.payment_guarantor_discount_id = payment_guarantor_discount_id.id
        elif res.payment == 'Employee':
            #Employee
            domain = [
                ('payment','=', 'Employee')
            ]
            payment_quarantor_discount_id = self.env['payment.guarantor.discount'].search(domain, limit=1)
            if not payment_quarantor_discount_id:
                raise Warning(_('Payment Guarantor Discount not found'))
            res.payment_quarantor_discount_id = payment_quarantor_discount_id.id
        else:
            res.payment_quarantor_discount_id = False

        return res
