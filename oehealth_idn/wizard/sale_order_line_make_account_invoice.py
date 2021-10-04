# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
# [GCC 8.4.0]
# Embedded file name: D:\Workspaces\Odoo10\mod\Health\addons-custom\oehealth_idn\wizard\sale_order_line_make_account_invoice.py
# Compiled at: 2018-10-07 17:53:17
import odoo.addons.decimal_precision as dp
from odoo import _, api, exceptions, fields, models
import datetime

class SaleOrderLineMakeAccountInvoice(models.TransientModel):
    _name = 'sale.order.line.make.account.invoice'
    _description = 'Sale Order Line Make Account Invoice'

    @api.model
    def _check_valid_request_line(self, request_line_ids):
        company_id = False
        for line in self.env['sale.order.line'].browse(request_line_ids):
            if line.order_id.state != 'sale':
                raise exceptions.Warning(_('Sale Order %s is not confirm') % line.order_id.name)
            if line.invoice_check != 'paid':
                raise exceptions.Warning(_('Sale Order %s is not fully paid') % line.order_id.name)
            if line.fee_state:
                raise exceptions.Warning(_('The line has already been invoiced.'))
            line_company_id = line.order_id.company_id and line.order_id.company_id.id or False
            if company_id is not False and line_company_id != company_id:
                raise exceptions.Warning(_('You have to select lines from the same company.'))
            else:
                company_id = line_company_id

    @api.multi
    def make_account_invoice(self):
        sale_invoice_ids = self.env['sale.order.line'].browse(self._context.get('active_ids'))
        self._check_valid_request_line(self._context.get('active_ids'))
        medical_fee_account = self.env['sale.config.settings'].search([], limit=1, order='id desc').medical_fee_account
        if not medical_fee_account:
            raise exceptions.Warning('You have not configured Medical Fee Account')
        inv_id = self.env['account.invoice'].create({'type': 'in_invoice', 
           'partner_id': self.env.user.partner_id.id, 
           'account_id': self.env.user.partner_id.property_account_payable_id.id, 
           'date_invoice': datetime.datetime.today().date()})
        for row in sale_invoice_ids:
            line_inv_id = self.env['account.invoice.line'].create({'name': '%s - %s' % (row.name, row.doctor_id.name), 
               'account_id': medical_fee_account.id, 
               'quantity': 1, 
               'price_unit': row.purchase_price, 
               'invoice_id': inv_id.id})
            row.inv_line_id = line_inv_id.id

        return {'name': 'Medical Fee Invoice', 
           'view_type': 'form', 
           'view_mode': 'form', 
           'res_id': inv_id.id, 
           'res_model': 'account.invoice', 
           'type': 'ir.actions.act_window'}