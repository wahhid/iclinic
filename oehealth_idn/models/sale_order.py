# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
# [GCC 8.4.0]
# Embedded file name: D:\Workspaces\Odoo10\mod\Health\addons-klinik\oehealth_idn\models\sale_order.py
# Compiled at: 2019-04-29 01:37:36
from odoo import models, fields, api, _
from odoo.exceptions import Warning
import logging

_logger = logging.getLogger(__name__)

class sale_order(models.Model):
    _inherit = 'sale.order'
    PAYMENT_TYPE = [
        ('Personal', 'Personal'),
        ('Corporate', 'Corporate'),
        ('Insurance', 'Insurance')]

    arrival_id = fields.Many2one(comodel_name='oeh.medical.appointment.register.walkin', string='Arrival ID')
    arrival_txt = fields.Char(compute='set_arrival_id', string='Arrival #', store=True)
    reg_id = fields.Many2one(comodel_name='unit.registration', string='Reg ID')
    unit_id = fields.Many2one(comodel_name='unit.administration', related='reg_id.unit', string='Unit')
    payment = fields.Selection(related='reg_id.payment', store=True)
    payment_guarantor_discount_id = fields.Many2one(related='reg_id.payment_guarantor_discount_id')
    patient_id = fields.Many2one(comodel_name='oeh.medical.patient', string='Patient')
    doctor_id = fields.Many2one(comodel_name='oeh.medical.physician', string='Doctor', readonly=True, states={'draft': [('readonly', False)]})
    medical_record = fields.Char(string='Medical Record', related='patient_id.identification_code')
    attribute_value = fields.Many2one(comodel_name='product.attribute.value', string='Medical Record', related='pricelist_id.attribute_value', index=True)
    invoice_check = fields.Selection(string='Invoice State', related='invoice_ids.state', store=False)
    invoice_paid = fields.Float(string='Invoice Paid', compute='_get_invoiced_check', readonly=True, store=False)
    is_blacklist = fields.Boolean(related='patient_id.is_blacklist')
    partner_invoice_type = fields.Selection(related='partner_invoice_id.customer_type', store=True)
    payment = fields.Selection(PAYMENT_TYPE, string='Payment Guarantor', compute='get_payment', readonly=True)

    
    @api.one
    def get_payment(self):
        for data in self:
            self.payment = data.reg_id.payment
    
    @api.depends('reg_id')
    def set_arrival_id(self):
        for data in self:
            data.arrival_txt = data.reg_id.arrival_txt or '%s / %s' % (data.arrival_id.name, data.arrival_id.patient.name)

    @api.depends('invoice_check', 'invoice_ids.state')
    def _get_invoiced_check(self):
        for data in self:
            amount = 0
            for line in data.invoice_ids:
                if line.state != 'draft':
                    amount += line.amount_total - line.residual

            data.invoice_paid = amount

    @api.multi
    def _prepare_invoice(self):
        res = super(sale_order, self)._prepare_invoice()
        res.update({'patient': self.patient_id.id, 'arrival_id': self.arrival_id.id, 'reg_id': self.reg_id.id})
        return res


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            line.discount = 0.0
            line.discount_type = False
            _logger.info(line.product_id.name)
            if line.product_id.item_type == 'General Item':
                line.discount = line.order_id.payment_guarantor_discount_id.general_item
                line.discount_type = 'percent'
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            elif line.product_id.item_type == 'Medical Item':
                line.discount = line.order_id.payment_guarantor_discount_id.medical_item
                line.discount_type = 'percent'
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            elif line.product_id.item_type == 'Food Item':
                line.discount = line.order_id.payment_guarantor_discount_id.food_item
                line.discount_type = 'percent'
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            elif line.product_id.item_type == 'Medicine':
                line.discount = line.order_id.payment_guarantor_discount_id.medicine
                line.discount_type = 'percent'
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            elif line.product_id.item_type == 'Doctor':
                line.discount = line.order_id.payment_guarantor_discount_id.doctor
                line.discount_type = 'percent'
                payment = line.order_id.payment_guarantor_discount_id.payment
                line.price_unit = self.order_id.doctor_id.consultancy_price
                if payment == 'Insurance':
                    insurance_type_id = line.order_id.payment_guarantor_discount_id.insurance_type_id
                    if insurance_type_id.is_bpjs:
                        line.price_unit = self.order_id.doctor_id.bpjs_price
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                    
            elif line.product_id.item_type == 'Nurse':
                line.discount = line.order_id.payment_guarantor_discount_id.nurse
                line.discount_type = 'percent'
           
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    arrival_id = fields.Many2one(comodel_name='oeh.medical.appointment.register.walkin', string='Arrival ID', related='order_id.arrival_id')
    reg_id = fields.Many2one(comodel_name='unit.registration', string='Reg ID', related='order_id.reg_id')
    patient_id = fields.Many2one(comodel_name='oeh.medical.patient', related='order_id.patient_id', string='Patient', store=True)
    doctor_id = fields.Many2one(comodel_name='oeh.medical.physician', related='order_id.doctor_id', string='Doctor', store=True)
    prescribe_qty = fields.Float(string='Prescribe Qty')
    qty_available = fields.Float(related='product_id.qty_available')
    product_type = fields.Selection(related='product_id.type')
    auto_billing = fields.Boolean(related='product_id.auto_billing')
    invoice_check = fields.Selection(related='order_id.invoice_check')
    inv_line_id = fields.Many2one(comodel_name='account.invoice.line', string='Invoice Line')
    fee_state = fields.Selection(related='inv_line_id.invoice_id.state', string='Fee State', store=True)
    consultancy_fee = fields.Float('Consultancy Fee (%)', default=0.0)
    bpjs_price =  fields.Float('Bpsj Charge', default=0.0)
    is_concoction = fields.Boolean('Concoction', default=False, readonly=True)
    medical_concoction_id = fields.Many2one('medical.concoction', 'Concoction #') 

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(sale_order_line, self)._prepare_invoice_line(qty)
        res.update({'patient_id': self.reg_id.patient.id, 'reg_id': self.reg_id.id, 'arrival_id': self.arrival_id.id})
        return res


class SaleReport(models.Model):
    _inherit = 'sale.report'
    doctor_id = fields.Many2one('oeh.medical.physician', string='Doctor', readonly=True)
    partner_invoice_type = fields.Selection([('Personal', 'Personal'), ('Company', 'Company'), ('Insurance', 'Insurance')], string='Customer Type', store=True)

    def _select(self):
        return super(SaleReport, self)._select() + ', l.doctor_id as doctor_id, s.partner_invoice_type as partner_invoice_type'

    def _group_by(self):
        return super(SaleReport, self)._group_by() + ', l.doctor_id, s.partner_invoice_type'