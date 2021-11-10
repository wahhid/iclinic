# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
# [GCC 8.4.0]
# Embedded file name: D:\Workspaces\Odoo10\mod\Health\addons-custom\oehealth_idn\models\product.py
# Compiled at: 2019-01-08 14:54:26
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, tools, _



class product_template(models.Model):
    _inherit = 'product.template'

    ITEM_TYPE = [
        ('General Item', 'General Item'),
        ('Medical Item', 'Medical Item'),
        ('Lab Item','Lab Item'),
        ('Food Item', 'Food Item'),
        ('Medicine', 'Medicine'),
        ('Doctor', 'Doctor'),
        ('Nurse', 'Nurse')
    ]

    item_type = fields.Selection(ITEM_TYPE, string='Item Type')
    is_concoction = fields.Boolean(string='Is Concoction ?')
    zat_uom = fields.Many2one('product.uom', string='Zat Active UoM')
    unit_ids = fields.Many2many('unit.administration', 'unit_product_rel', 'product_id', 'unit_id', string='Units')
    default_code = fields.Char(index=True)
    list_price = fields.Float(index=True)
    uom_id = fields.Many2one(index=True)
    uom_po_id = fields.Many2one(index=True)
    product_template_categ_id = fields.Many2one(
        'product.template.category', string='Product Template Category',
        help="Those categories are used to group similar products for point of sale.")


class product_product(models.Model):
    _inherit = 'product.product'
    auto_billing = fields.Boolean(string='Auto Billing ?', help='Auto add item in sale order line each arrival customer')
    admin_fee = fields.Boolean(string='Admin Fee ?', help='Reference product for invoice line each inpatient registration')
    stock_ids = fields.One2many('stock.quant', 'product_id', string='Qty On Hand')
    default_code = fields.Char(index=True)


class product_pricelist(models.Model):
    _inherit = 'product.pricelist'
    attribute_value = fields.Many2one(comodel_name='product.attribute.value', string='Attribute Value', help='Filter product by pricelist & attribute value', index=True)


class PaymentGuarantorDiscount(models.Model):
    _name  = 'payment.guarantor.discount'
    _decscription = 'Payment Guarantor Discount'
    _rec_name = 'description'

    PAYMENT_TYPE = [
        ('Personal', 'Personal'),
        ('Corporate', 'Corporate'),
        ('Insurance', 'Insurance'),
        ('Employee', 'Employee')
    ]

    ITEM_TYPE = [
        ('General Item', 'General Item'),
        ('Medical Item', 'Medical Item'),
        ('Food Item', 'Food Item'),
        ('Medicine', 'Medicine'),
        ('Doctor', 'Doctor'),
        ('Nurse', 'Nurse')
    ]

    def get_description(self):
        for row in self:
            if row.payment == 'Corporate':
                row.description = row.payment + " - " + row.company.name
            elif row.payment == 'Insurance':
                row.description = row.payment + " - " + row.insurance_type_id.name
            else:
                row.description = row.payment

    description = fields.Char("Description", size=255, compute=get_description)
    payment = fields.Selection(PAYMENT_TYPE, string='Payment Guarantor', default='Personal', track_visibility='onchange')
    company = fields.Many2one(comodel_name='res.partner', string='Company', track_visibility='onchange')
    insurance_type_id = fields.Many2one('medical.insurance.type', 'Insurance Type',  track_visibility='onchange')
    general_item = fields.Float('General Item in %')
    medical_item = fields.Float('Medical Item in %')
    food_item = fields.Float('Food Item in %')
    medicine = fields.Float('Medicine in %')
    doctor = fields.Float('Doctor in %')
    nurse = fields.Float('Nurse in %')



class ProductTemplateCategory(models.Model):
    _name = "product.template.category"
    _description = "Public Category"
    _order = "sequence, name"

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValueError(_('Error ! You cannot create recursive categories.'))

    name = fields.Char(required=True, translate=True)
    parent_id = fields.Many2one('product.template.category', string='Parent Category', index=True)
    child_id = fields.One2many('product.template.category', 'parent_id', string='Children Categories')
    sequence = fields.Integer(help="Gives the sequence order when displaying a list of product categories.")
    # NOTE: there is no 'default image', because by default we don't show
    # thumbnails for categories. However if we have a thumbnail for at least one
    # category, then we display a default image on the other, so that the
    # buttons have consistent styling.
    image = fields.Binary(attachment=True,
        help="This field holds the image used as image for the cateogry, limited to 1024x1024px.")
    image_medium = fields.Binary(string="Medium-sized image", attachment=True,
        help="Medium-sized image of the category. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved. "
             "Use this field in form views or some kanban views.")
    image_small = fields.Binary(string="Small-sized image", attachment=True,
        help="Small-sized image of the category. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required.")

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        return super(ProductTemplateCategory, self).create(vals)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        return super(ProductTemplateCategory, self).write(vals)

    @api.multi
    def name_get(self):
        def get_names(cat):
            res = []
            while cat:
                res.append(cat.name)
                cat = cat.parent_id
            return res
        return [(cat.id, " / ".join(reversed(get_names(cat)))) for cat in self]
