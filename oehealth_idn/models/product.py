# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
# [GCC 8.4.0]
# Embedded file name: D:\Workspaces\Odoo10\mod\Health\addons-custom\oehealth_idn\models\product.py
# Compiled at: 2019-01-08 14:54:26
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _

class product_template(models.Model):
    _inherit = 'product.template'
    ITEM_TYPE = [
     ('Medicine', 'Medicine'),
     ('Medical Item', 'Medical Item'),
     ('General Item', 'General Item'),
     ('Food Item', 'Food Item')]
    item_type = fields.Selection(ITEM_TYPE, string='Item Type')
    is_concoction = fields.Boolean(string='Is Concoction ?')
    zat_uom = fields.Many2one('product.uom', string='Zat Active UoM')
    unit_ids = fields.Many2many('unit.administration', 'unit_product_rel', 'product_id', 'unit_id', string='Units')
    default_code = fields.Char(index=True)
    list_price = fields.Float(index=True)
    uom_id = fields.Many2one(index=True)
    uom_po_id = fields.Many2one(index=True)


class product_product(models.Model):
    _inherit = 'product.product'
    auto_billing = fields.Boolean(string='Auto Billing ?', help='Auto add item in sale order line each arrival customer')
    admin_fee = fields.Boolean(string='Admin Fee ?', help='Reference product for invoice line each inpatient registration')
    stock_ids = fields.One2many('stock.quant', 'product_id', string='Qty On Hand')
    default_code = fields.Char(index=True)


class product_pricelist(models.Model):
    _inherit = 'product.pricelist'
    attribute_value = fields.Many2one(comodel_name='product.attribute.value', string='Attribute Value', help='Filter product by pricelist & attribute value', index=True)