# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError


class WizardPhysicianIncomeReport(models.TransientModel):
    _name = 'wizard.physician.income.report'
    _description = 'Wizard physician Income Report'

    start_date = fields.Date(required=True, default=fields.Date.today)
    end_date = fields.Date(required=True, default=fields.Date.today)
    physician_ids = fields.Many2many('oeh.medical.physician', 'clinic_detail_physicians',
        default=lambda s: s.env['oeh.medical.physician'].search([]))

    @api.onchange('start_date')
    def _onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.end_date = self.start_date

    @api.onchange('end_date')
    def _onchange_end_date(self):
        if self.end_date and self.end_date < self.start_date:
            self.start_date = self.end_date

    @api.multi
    def generate_report(self):
        data = {'date_start': self.start_date, 'date_stop': self.end_date, 'physician_ids': self.physician_ids.ids}
        return self.env['report'].get_action([], 'oehealth_idn.report_physiciandetails', data=data)