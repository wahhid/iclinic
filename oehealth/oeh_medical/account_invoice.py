# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
# [GCC 8.4.0]
# Embedded file name: D:\DEV\Workspaces\odoo10\addons_custom\oehealth\oeh_medical\account_invoice.py
# Compiled at: 2017-10-14 16:33:18
from odoo import api, SUPERUSER_ID, fields, models, _

class account_invoice(models.Model):
    _inherit = 'account.invoice'
    patient = fields.Many2one('oeh.medical.patient', string='Related Patient', help='Patient Name')