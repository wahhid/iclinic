# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
# [GCC 8.4.0]
# Embedded file name: D:\DEV\Workspaces\odoo10\addons_custom\oehealth\oeh_medical\oeh_medical_ethnic_groups.py
# Compiled at: 2017-10-14 16:33:18
from odoo import fields, models

class OeHealthEthnicGroups(models.Model):
    _name = 'oeh.medical.ethnicity'
    _description = 'Ethnic Groups'
    name = fields.Char(string='Ethnic Groups', size=256, required=True)
    _sql_constraints = [
     ('name_uniq', 'unique (name)', 'The ethnic group must be unique !')]