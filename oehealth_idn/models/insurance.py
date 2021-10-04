# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
# [GCC 8.4.0]
# Embedded file name: D:\Workspaces\Odoo10\mod\Health\addons-custom\oehealth_idn\models\insurance.py
# Compiled at: 2019-01-08 14:17:25
from odoo import models, fields, api, _

class HealthInsuranceType(models.Model):
    _name = 'medical.insurance.type'
    _description = 'Insurance Types'
    name = fields.Char(string='Types', size=256, required=True)
    partner_id = fields.Many2one(comodel_name='res.partner', string='Payment Guarantor', required=True)
    admin_fee = fields.Float(string='Admin Fee Percentage (%)', default=8)
    max_admin_fee = fields.Float(string='Max Admin Fee')
    active = fields.Boolean(string='Active', default=True)
    is_bpjs = fields.Boolean('Is BPSJ', default=False)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The insurance type must be unique')
    ]


class HealthInsurance(models.Model):
    _name = 'medical.insurance'
    _description = 'Insurances'
    STATE = [
     ('Draft', 'Draft'),
     ('Active', 'Active'),
     ('Expired', 'Expired')]
    ins_no = fields.Char(string='Insurance No.', size=64, required=True)
    patient = fields.Many2one('oeh.medical.patient', string='Patient', required=True)
    start_date = fields.Date(string='Start Date', required=False)
    exp_date = fields.Date(string='Expiration date', required=False)
    ins_type = fields.Many2one('medical.insurance.type', string='Insurance Type', required=True)
    info = fields.Text(string='Extra Info')
    state = fields.Selection(STATE, string='State', readonly=True, copy=False, help='Status of insurance', default=lambda *a: 'Draft')
    _defaults = {'is_insurance_company': True, 
       'state': 'Draft'}

    @api.model
    def create(self, vals):
        vals['is_insurance_company'] = True
        insurance = super(HealthInsurance, self).create(vals)
        return insurance

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            tit = '[%s] %s' % (record.ins_no, record.ins_type.name)
            res.append((record.id, tit))

        return res

    @api.multi
    def make_active(self):
        self.write({'state': 'Active'})
        return True