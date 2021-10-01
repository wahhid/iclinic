# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
# [GCC 8.4.0]
# Embedded file name: D:\Workspaces\Odoo10\mod\Health\addons-custom\oehealth_idn\models\room.py
# Compiled at: 2019-01-07 04:56:00
from odoo import models, fields, api, _
from odoo.exceptions import Warning

class oeh_medical_health_center_ward(models.Model):
    _inherit = 'oeh.medical.health.center.ward'
    class_id = fields.Many2one(comodel_name='class.administration', string='Class')
    unit = fields.Many2one(comodel_name='unit.administration', string='Unit')
    bed_capacity = fields.Integer(string='Bed Capacity')

    @api.multi
    def generate_bed(self):
        for row in self:
            if not row.bed_capacity:
                raise Warning('Bed Capacity Required !')
            bed = row.env['oeh.medical.health.center.beds']
            for no in range(row.bed_count, row.bed_capacity):
                vals = {'name': row.name + ' [Bed ' + str(no + 1) + ']', 'institution': row.institution.id, 
                   'building': row.building.id, 
                   'ward': row.id, 
                   'bed_type': 'Gatch Bed', 
                   'list_price': row.class_id.price, 
                   'type': 'service'}
                bed.create(vals)


class oeh_medical_health_center_beds(models.Model):
    _inherit = 'oeh.medical.health.center.beds'
    ward = fields.Many2one('oeh.medical.health.center.ward', string='Room', domain="[('building', '=', building)]", help='Ward or room', ondelete='cascade')
    unit = fields.Many2one(related='ward.unit', string='Unit', store=True)
    reg_ids = fields.One2many('unit.registration', 'bed', string='Reg IDs')
    reg_id = fields.Many2one(comodel_name='unit.registration', string='Registration ID')
    patient = fields.Many2one(related='reg_id.patient', string='Patient')
    doctor = fields.Many2one(related='reg_id.doctor', string='Doctor', store=True)
    admission_date = fields.Datetime(related='reg_id.admission_date', string='Check-In Date')