# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError


class WizardOwlexaInvoice(models.TransientModel):
    _name = 'wizard.owlexa.invoice'
    _description = 'Owlexa Invoice'

    account_invoice_ids = fields.Many2many('account.invoice', default=lambda s: s.env['account.invoice'].search([]))

    @api.multi
    def add_invoice(self):
        pass