# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
# [GCC 8.4.0]
# Embedded file name: D:\Workspaces\Odoo10\mod\Health\addons-custom\oehealth_idn\models\prescription.py
# Compiled at: 2018-11-22 17:20:13
from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
import datetime

class oeh_medical_prescription(models.Model):
    _inherit = 'oeh.medical.prescription'

    def action_prescription_send_to_pharmacy(self):
        pharmacy_obj = self.env['oeh.medical.health.center.pharmacy.line']
        pharmacy_line_obj = self.env['oeh.medical.health.center.pharmacy.prescription.line']
        res = {}
        for pres in self:
            if not pres.pharmacy:
                raise UserError(_('No pharmacy selected !!'))
            else:
                curr_pres = {'name': pres.id, 
                   'patient': pres.patient.id, 
                   'doctor': pres.doctor.id, 
                   'pharmacy_id': pres.pharmacy.id, 
                   'state': 'Draft', 
                   'arrival_id': pres.walkin.id, 
                   'reg_id': pres.reg_id.id}
                phy_ids = pharmacy_obj.create(curr_pres)
                if phy_ids:
                    if pres.prescription_line:
                        for ps in pres.prescription_line:
                            curr_pres_line = {'name': ps.name.id, 'indication': ps.indication.id, 
                               'price_unit': ps.name.list_price, 
                               'qty': ps.qty, 
                               'actual_qty': ps.qty, 
                               'prescription_id': phy_ids.id, 
                               'state': 'Draft'}
                            pharmacy_line_obj.create(curr_pres_line)

                res = self.write({'state': 'Sent to Pharmacy'})

        return True


class oeh_medical_prescription_line(models.Model):
    _inherit = 'oeh.medical.prescription.line'
    name = fields.Many2one('product.product', string='Medicines', help='Prescribed Medicines', domain=[('item_type', '=', 'Medicine')], required=True)


class oeh_medical_health_center_pharmacy_line(models.Model):
    _inherit = 'oeh.medical.health.center.pharmacy.line'
    
    arrival_id = fields.Many2one(comodel_name='oeh.medical.appointment.register.walkin', string='Queue #')
    reg_id = fields.Many2one(comodel_name='unit.registration', string='Reference Reg ID')
    unit_id = fields.Many2one(comodel_name='unit.administration', related='reg_id.unit', string='Reference Unit')
    reg_ids = fields.Many2one(comodel_name='unit.registration', string='Registration')
    sale_order_id = fields.Many2one('sale.order', string='Order#')

    @api.multi
    def create_sale(self):
        obj = self.env['sale.order']
        obj2 = self.env['unit.registration']
        line_obj = self.env['sale.order.line']
        inv_ids = []
        guarantor = 0
        arrival = 0
        for acc in self:
            user_unit = self.env['unit.administration'].search([('operating_id', '=', self.env.user.default_operating_unit_id.id)], limit=1).id
            if user_unit:
                val_obj2 = {
                    'reference_id': acc.reg_id.id, 
                    'support_walkin_id': acc.arrival_id.id, 
                    'patient': acc.patient.id or acc.arrival_id.patient.id, 
                    'type': 'Medical Support', 
                    'payment': acc.reg_id.payment, 
                    'company': acc.reg_id.company.id, 
                    'insurance': acc.reg_id.insurance.id, 
                    'doctor': acc.doctor.id, 
                    'unit': user_unit, 
                    'date': datetime.datetime.now()
                }
                reg_ids = obj2.create(val_obj2)
                acc.reg_ids = reg_ids
            else:
                raise UserError(_('Configuration Error! \n Could not Find default Operating Unit in User : ' + self.env.user.name))
            
            if reg_ids:
                if reg_ids.payment == 'Insurance':
                    guarantor = reg_ids.insurance.ins_type.partner_id.id
                elif reg_ids.payment == 'Corporate':
                    guarantor = reg_ids.company.id
                else:
                    guarantor = reg_ids.patient.partner_id.id
                
                val_obj = {'reg_id': reg_ids.id, 
                   'arrival_id': acc.arrival_id.id, 
                   'patient_id': reg_ids.patient.id, 
                   'doctor_id': reg_ids.doctor.id, 
                   'partner_id': reg_ids.patient.partner_id.id, 
                   'partner_invoice_id': guarantor, 
                   'partner_shipping_id': reg_ids.patient.partner_id.id, 
                   'pricelist_id': reg_ids.charge_id.pricelist.id or reg_ids.patient.partner_id.property_product_pricelist.id, 
                   'location_id': self.env['stock.location'].search([('unit_ids.operating_id', '=', self.env.user.default_operating_unit_id.id)], limit=1).id}
                inv_ids = obj.create(val_obj)
                if inv_ids:
                    inv_id = inv_ids.id
                    if self.arrival_id and not self.arrival_id.have_register:
                        product = self.env['product.product'].search([('auto_billing', '!=', False)])
                        for p in product:
                            vals = {'order_id': inv_id, 'product_id': p.id, 
                               'name': p.name, 
                               'product_uom_qty': 1, 
                               'product_uom': p.uom_id.id, 
                               'price_unit': p.lst_price}
                            line_obj.create(vals)

                        arrival = self.env['oeh.medical.appointment.register.walkin'].browse(self.arrival_id.id)
                        arrival.write({'have_register': True})
                    if acc.prescription_lines:
                        for ps in acc.prescription_lines:
                            vals = {'order_id': inv_id, 
                               'product_id': ps.name.id, 
                               'name': ps.name.name, 
                               'prescribe_qty': ps.qty, 
                               'product_uom_qty': ps.actual_qty, 
                               'product_uom': ps.name.uom_id.id, 
                               'price_unit': ps.price_unit}
                            line_obj.create(vals)

                self.write(
                    {
                        'state': 'Invoiced',
                        'sale_order_id': inv_id
                    }
                )
            else:
                raise UserError(_('Configuration Error! \n Could not Find Registration to Create the Transactions !'))


class oeh_medical_health_center_pharmacy_prescription_line(models.Model):
    _inherit = 'oeh.medical.health.center.pharmacy.prescription.line'
    name = fields.Many2one('product.product', string='Medicines', help='Prescribed Medicines', domain=[('item_type', '=', 'Medicine')], required=True)
    qty_available = fields.Float(related='name.qty_available')