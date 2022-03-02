# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00)
# [GCC 8.4.0]
# Embedded file name: D:\Workspaces\Odoo10\mod\Health\addons-klinik-online\oehealth_idn\models\unit_registration.py
# Compiled at: 2019-07-28 17:50:56
from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
from datetime import timedelta


class pathology_diagnostic(models.Model):
    _inherit = 'oeh.medical.pathology'

    reg_id = fields.Many2one(comodel_name='unit.registration', string='Reg ID #')
    eval_id = fields.Many2one(comodel_name='oeh.medical.evaluation', string='Evaluation ID #')
