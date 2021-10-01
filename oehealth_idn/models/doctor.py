# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
# [GCC 8.4.0]
# Embedded file name: D:\Workspaces\Odoo10\mod\Health\addons-custom\oehealth_idn\models\doctor.py
# Compiled at: 2018-11-01 17:02:59
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _

class oeh_medical_physician(models.Model):
    _inherit = 'oeh.medical.physician'

    @api.multi
    def _app_count(self):
        for pa in self:
            oe_apps = pa.env['oeh.medical.appointment'].search_count([('doctor', '=', pa.id), ('state', '=', 'Scheduled')])
            pa.app_count = oe_apps

        return True

    unit_ids = fields.Many2many('unit.administration', 'unit_doctor_rel', 'doctor_id', 'unit_id', string='Doctor Units')
    app_count = fields.Integer(compute=_app_count, string='Appointments')
    queue_code = fields.Char(string='Queue Code')

    @api.multi
    def view_schedule(self):
        return {'domain': "[('physician_id','=', " + str(self.id) + ')]', 
           'name': 'Daily Schedule', 
           'view_type': 'form', 
           'view_mode': 'tree,form', 
           'res_model': 'oeh.medical.physician.walkin.schedule', 
           'type': 'ir.actions.act_window'}


class OeHealthPhysicianWalkinSchedule(models.Model):
    _inherit = 'oeh.medical.physician.walkin.schedule'
    replacement_doctor = fields.Many2one('oeh.medical.physician', string='Replacement Doctor')