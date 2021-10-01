# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
# [GCC 8.4.0]
# Embedded file name: D:\DEV\Workspaces\odoo10\addons_custom\oehealth\oeh_medical\product_product.py
# Compiled at: 2017-10-14 16:33:18
from odoo import api, fields, models, _

class oeHealthProduct(models.Model):
    _inherit = 'product.template'
    is_medicine = fields.Boolean(string='Medicine', help='Check if the product is a medicine')
    is_bed = fields.Boolean(string='Bed', help='Check if the product is a bed')
    is_vaccine = fields.Boolean(string='Vaccine', help='Check if the product is a vaccine')
    is_medical_supply = fields.Boolean(string='Medical Supply', help='Check if the product is a medical supply')
    is_insurance_plan = fields.Boolean(string='Insurance Plan', help='Check if the product is an insurance plan')