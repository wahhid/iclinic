# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
# [GCC 8.4.0]
# Embedded file name: D:\Workspaces\Odoo10\mod\Health\addons-comcustom\oehealth\oeh_medical\oeh_medical_insurance.py
# Compiled at: 2018-04-17 04:37:55
from odoo import api, fields, models, _

class OeHealthInsuranceType(models.Model):
    _name = 'oeh.medical.insurance.type'
    _description = 'Insurance Types'
    name = fields.Char(string='Types', size=256, required=True)
    _sql_constraints = [
     ('name_uniq', 'unique (name)', 'The insurance type must be unique')]


class OeHealthInsurance(models.Model):
    _name = 'oeh.medical.insurance'
    _description = 'Insurances'
    _inherits = {'res.partner': 'partner_id'}
    STATE = [
     ('Draft', 'Draft'),
     ('Active', 'Active'),
     ('Expired', 'Expired')]
    partner_id = fields.Many2one('res.partner', string='Related Partner', required=True, ondelete='cascade', help='Partner-related data of the insurance company')
    ins_no = fields.Char(string='Insurance #', size=64, required=True)
    patient = fields.Many2one('oeh.medical.patient', string='Patient', required=True)
    start_date = fields.Date(string='Start Date', required=True)
    exp_date = fields.Date(string='Expiration date', required=True)
    ins_type = fields.Many2one('oeh.medical.insurance.type', string='Insurance Type', required=True)
    info = fields.Text(string='Extra Info')
    state = fields.Selection(STATE, string='State', readonly=True, copy=False, help='Status of insurance', default=lambda *a: 'Draft')
    _defaults = {'is_insurance_company': True, 
       'state': 'Draft'}

    @api.model
    def create(self, vals):
        vals['is_insurance_company'] = True
        insurance = super(OeHealthInsurance, self).create(vals)
        return insurance

    @api.multi
    @api.depends('name', 'ins_no')
    def name_get(self):
        res = []
        for record in self:
            name = self.name
            if self.ins_no:
                name = '[' + self.ins_no + '] ' + name
            res += [(record.id, name)]

        return res

    @api.multi
    def make_active(self):
        self.write({'state': 'Active'})
        return True