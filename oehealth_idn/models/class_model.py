# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
# [GCC 8.4.0]
# Embedded file name: D:\Workspaces\Odoo10\mod\addons-health\oehealth_idn\models\class_model.py
# Compiled at: 2018-03-23 17:25:59
from odoo import models, fields, api, _

class class_administration(models.Model):
    
    _name = 'class.administration'
    name = fields.Char(string='Class Name')
    type = fields.Selection([('Out-Patient', 'Out-Patient'), ('In-Patient', 'In-Patient')], 'Unit Type')
    price = fields.Integer(string='Price Per Day')
    pricelist = fields.Many2one(comodel_name='product.pricelist', string='Pricelist')
    remarks = fields.Char(string='Class Remarks')