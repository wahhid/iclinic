# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
# [GCC 8.4.0]
# Embedded file name: D:\DEV\Workspaces\odoo10\addons_custom\oehealth\oeh_medical\res_partner.py
# Compiled at: 2017-10-14 16:33:18
from odoo import api, fields, models, _

class oeHealthPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _description = 'Partner'
    
    is_insurance_company = fields.Boolean(string='Insurance Company', help='Check if the party is an Insurance Company')
    is_institution = fields.Boolean(string='Institution', help='Check if the party is a Medical Center')
    is_doctor = fields.Boolean(string='Health Professional', help='Check if the party is a health professional')
    is_patient = fields.Boolean(string='Patient', help='Check if the party is a patient')
    is_person = fields.Boolean(string='Person', help='Check if the party is a person.')
    is_pharmacy = fields.Boolean(string='Pharmacy', help='Check if the party is a Pharmacy')
    ref = fields.Char(size=256, string='SSN', help='Patient Social Security Number or equivalent')