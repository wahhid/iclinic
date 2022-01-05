# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
# [GCC 8.4.0]
# Embedded file name: D:\Workspaces\Odoo10\mod\Health\addons-custom\oehealth_idn\models\account_invoice.py
# Compiled at: 2019-01-09 17:38:07
from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    arrival_id = fields.Many2one(comodel_name='oeh.medical.appointment.register.walkin', string='Arrival ID')
    reg_id = fields.Many2one(comodel_name='unit.registration', string='Reg ID')
    medical_record = fields.Char(string='Medical Record', related='patient.identification_code')
    amount_pay = fields.Float(string='Amount Pay')
    amount_change = fields.Float(string='Change', compute='get_change')

    @api.depends('amount_pay')
    def get_change(self):
        for row in self:
            if row.amount_pay and row.residual:
                row.amount_change = row.amount_pay - row.residual
            else:
                row.amount_change = row.amount_pay - row.amount_total

    @api.multi
    def action_invoice_paid(self):
        to_pay_invoices = self.filtered(lambda inv: inv.state != 'paid')
        if to_pay_invoices.filtered(lambda inv: inv.state != 'open'):
            raise UserError(_('Invoice must be validated in order to set it to register payment.'))
        if to_pay_invoices.filtered(lambda inv: not inv.reconciled):
            raise UserError(_('You cannot pay an invoice which is partially paid. You need to reconcile payment entries first.'))
        if self.arrival_id:
            reg = self.env['oeh.medical.appointment.register.walkin'].browse(self.arrival_id.id)
            reg.write({'state': 'Completed'})
        return to_pay_invoices.write({'state': 'paid'})

    @api.multi
    def admin_fee(self):
        inv_line = self.env['account.invoice.line']
        inpatient = False
        for line in self.invoice_line_ids:
            if line.reg_id.type == 'In-Patient':
                inpatient = True
                arrival_id = line.arrival_id
                reg_id = line.reg_id

        if inpatient:
            product = self.env['product.product'].search([('admin_fee', '!=', False)])
            if product:
                for p in product:
                    inv_line.search([('invoice_id', '=', self.id), ('product_id', '=', p.id)]).unlink()
                    admin_fee_percent = 1
                    max_admin_fee = 0.0
                    ins = self.env['medical.insurance.type'].search([('partner_id', '=', self.partner_id.id)], limit=1)
                    if ins:
                        admin_fee_percent = ins.admin_fee
                        max_admin_fee = ins.max_admin_fee
                    else:
                        prv = self.env['medical.insurance.type'].search([('name', '=', 'Personal')], limit=1)
                        if prv:
                            admin_fee_percent = prv.admin_fee
                            max_admin_fee = prv.max_admin_fee
                        else:
                            raise UserError('Medical Insurance Type "Personal" Not Found!')
                            
                    admin_fee_value = self.amount_total * admin_fee_percent / 100
                    if max_admin_fee and admin_fee_value >= max_admin_fee:
                        admin_fee_value = max_admin_fee
                    else:
                        admin_fee_value = admin_fee_value
                    vals = {'invoice_id': self.id, 
                       'arrival_id': arrival_id.id, 
                       'reg_id': reg_id.id, 
                       'product_id': p.id, 
                       'name': p.name + ' ' + str(int(admin_fee_percent)) + '%', 
                       'account_id': p.property_account_income_id.id or p.categ_id.property_account_income_categ_id.id, 
                       'quantity': 1, 
                       'uom_id': p.uom_id.id, 
                       'price_unit': admin_fee_value}
                    adm_id = inv_line.create(vals)

            else:
                raise Warning('Product Administration Fee Label Not Found!')


class account_invoice_line(models.Model):
    _inherit = 'account.invoice.line'

    arrival_id = fields.Many2one(comodel_name='oeh.medical.appointment.register.walkin', string='Arrival ID')
    reg_id = fields.Many2one(comodel_name='unit.registration', string='Reg ID')
    patient_id = fields.Many2one(comodel_name='oeh.medical.patient', string='Patient')


class account_payment(models.Model):
    _inherit = 'account.payment'
    amount_pay = fields.Float(string='Amount Pay')
    amount_change = fields.Float(string='Change', compute='get_change')

    @api.depends('amount_pay', 'amount')
    def get_change(self):
        for row in self:
            if row.amount_pay:
                row.amount_change = row.amount_pay - row.amount
            if row.amount_change < 0:
                raise Warning('Amount Pay less than Payment Amount, Please Change Payment Amount!')