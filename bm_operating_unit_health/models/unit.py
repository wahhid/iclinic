# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
# [GCC 8.4.0]
# Embedded file name: /opt/odoo-10/addons-health/bm_operating_unit_health/models/unit.py
# Compiled at: 2019-02-09 09:22:44
from odoo import models, fields, api, _

class unit_administration(models.Model):
    _name = 'unit.administration'
    #_inherits = {'operating.unit': 'operating_id'}

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, '%s - %s' % (rec.name,rec.operating_id.name)))
        return result

    name = fields.Char('Name', size=200)
    code = fields.Char('Code', size=20)
    operating_id = fields.Many2one('operating.unit', string='Operating Units', required=True, ondelete='cascade')
    color = fields.Integer(string='Color')
    type = fields.Selection([('Out-Patient', 'Out-Patient'),
     ('In-Patient', 'In-Patient'),
     ('Emergency', 'Emergency'),
     ('Medical Support', 'Medical Support'),
     ('Logistic', 'Logistic'),
     ('Non-Medis', 'Non-Medis')], 'Unit Type')

    is_pharmacy = fields.Boolean(string='Is Pharmacy?')
    is_radiology = fields.Boolean(string='Is Radiology?')
    is_laboratorium = fields.Boolean(string='Is Laboratorium?')
    is_perina = fields.Boolean(string='Is Perina?')
    have_doctor = fields.Boolean(string='Have Doctor?')
    unit_remarks = fields.Char(string='Unit Remarks')


class operating_unit(models.Model):
    _inherit = 'operating.unit'
    
    unit_administration_ids = fields.One2many('unit.administration','operating_id', 'Units')
#     type = fields.Selection([('Out-Patient', 'Out-Patient'),
#      ('In-Patient', 'In-Patient'),
#      ('Emergency', 'Emergency'),
#      ('Medical Support', 'Medical Support'),
#      ('Logistic', 'Logistic'),
#      ('Non-Medis', 'Non-Medis')], 'Unit Type')