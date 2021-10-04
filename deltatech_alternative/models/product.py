# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2015 Deltatech All Rights Reserved
#                    Dorin Hongu <dhongu(@)gmail(.)com       
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import Warning, RedirectWarning


class product_catalog(models.Model):
    _name = "product.catalog"
    _description = "Product catalog"

    name = fields.Char(string='Name', index=True)
    code = fields.Char(string='Code', index=True)
    code_new = fields.Char(string='Code New', index=True)
    list_price = fields.Float(string='Sale Price', required=True, digits=dp.get_precision('Product Price'))
    categ_id = fields.Many2one('product.category', string='Internal Category', required=True,
                               domain="[('type','=','normal')]", help="Select category for the current product")
    supplier_id = fields.Many2one('res.partner', string='Supplier')
    product_id = fields.Many2one('product.product', string='Product', ondelete='set null')
    purchase_delay = fields.Integer(string="Purchase delay")
    sale_delay = fields.Integer(string="Sale delay")
    # list_price_currency_id = fields.Many2one('res.currency',  string='Currency List Price', help="Currency for list price." , compute='_compute_currency_id' )


    """
    @api.one
    def _compute_currency_id(self):            
        price_type = self.env['product.price.type'].search([('field','=','list_price')]) 
        if price_type:
            self.list_price_currency_id = price_type.currency_id
        else:
            self.list_price_currency_id = self.env.user.company_id
    """

    @api.multi
    def create_product(self):
        prod = self.env['product.product']
        for prod_cat in self:
            if (not prod_cat.code_new or len(prod_cat.code_new) < 2) and not prod_cat.product_id:

                route_ids = []
                mto = self.env.ref('stock.route_warehouse0_mto', raise_if_not_found=False)

                if mto:
                    route_ids += [mto.id]
                buy = self.env.ref('purchase.route_warehouse0_buy', raise_if_not_found=False)
                if buy:
                    route_ids += [buy.id]

                values = {'name': prod_cat.name,
                          'default_code': prod_cat.code,
                          'lst_price': prod_cat.list_price,
                          'categ_id': prod_cat.categ_id.id,
                          'route_ids': [(6, 0, route_ids)],
                          'sale_delay': prod_cat.sale_delay}
                if prod_cat.supplier_id:
                    values['seller_ids'] = [(0, 0, {'name': prod_cat.supplier_id.id,
                                                    'delay': prod_cat.purchase_delay})]
                old_code = prod_cat.get_echiv()
                if old_code:
                    alt = []
                    for old in old_code:
                        alt.append((0, 0, {'name': old.code}))
                    values['alternative_ids'] = alt

                prod_new = prod.with_context({'no_catalog': True}).search([('default_code', '=ilike', prod_cat.code)])
                if not prod_new:
                    prod_new = prod.sudo().create(values)

                prod_cat.sudo().write({'product_id': prod_new.id})

                prod += prod_new

        return prod

    @api.multi
    def get_echiv(self):
        res = self.env['product.catalog']
        for prod_cat in self:
            ids_old = self.search([('code_new', '=ilike', prod_cat.code)])
            ids_very_old = ids_old.get_echiv()
            res = ids_old | ids_very_old
        return res

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Code must be unique !'),
    ]


class product_template(models.Model):
    _inherit = 'product.template'

    alternative_code = fields.Char(string='Alternative Code', index=True, compute='_compute_alternative_code')
    alternative_ids = fields.One2many('product.alternative', 'product_tmpl_id', string='Alternatives')
    # dimensions = fields.Char(string='Dimensions' )
    # shelf_life = fields.Char(string='Shelf Life' )
    # uom_shelf_life = fields.Many2one('product.uom', string='Unit of Measure Shelf Life', help="Unit of Measurer for Shelf Life" )
    used_for = fields.Char(string="Used For")

    @api.one
    @api.depends('alternative_ids')
    def _compute_alternative_code(self):
        codes = []
        for cod in self.alternative_ids:
            if cod.name:
                codes += [cod.name]
        # codes = self.alternative_ids.mapped('name')

        code = '; '.join(codes)
        self.alternative_code = code


class product_product(models.Model):
    _inherit = 'product.product'

    """
    @api.model
    @api.returns('self')
    def search(self,   args, offset=0, limit=None, order=None, context=None, count=False):
        #return models.Model.search(self, cr, user, args, offset=offset, limit=limit, order=order, context=context, count=count)
        res = models.Model.search(self,  args, offset=offset, limit=limit, order=order, context=context, count=count)
        
        if not res and not self.env.context.get('no_catalog',False):
            name = ''
            for opt in args:
                if isinstance(opt, tuple):
                    left, operator, right = opt
                    if left in ['name','default_code']:
                        name = right
            if name:
                res = self.search_in_catalog(name)  
        return res
    """

    @api.model
    def search_in_catalog(self, name):
        alt = []
        prod_cat = False
        res = None
        while name and len(name) > 2:
            prod_cat = self.env['product.catalog'].search([('code', '=ilike', name)], limit=1)
            if prod_cat:
                alt.append(name)
                name = prod_cat.code_new
            else:
                name = ''
        if prod_cat:
            if not prod_cat.product_id:
                prod_new = prod_cat.create_product()
                res = prod_new
            else:
                res = prod_cat.product_id
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        res_alt = []
        if name and len(name) > 2:
            alternative_ids = self.env['product.alternative'].search([('name', 'ilike', name)], limit=10)
            # ids = []
            products = self.env['product.product']
            for alternative in alternative_ids:
                # ids += alternative.product_tmpl_id.product_variant_ids.ids
                products = products | alternative.product_tmpl_id.product_variant_ids
            if products:
                # recs = self.search([('id', 'in', ids )], limit=limit)
                # res_alt =  recs.name_get()
                res_alt = products.name_get()

        this = self.with_context({'no_catalog': True})
        res = super(product_product, this).name_search(name, args, operator=operator, limit=limit) + res_alt

        prod_cat_ids = None
        if not res:
            prod = self.search_in_catalog(name)
            if prod:
                res = prod.name_get()

        return res


class product_alternative(models.Model):
    _name = "product.alternative"
    _description = "Product alternative"

    name = fields.Char(string='Code', index=True)
    sequence = fields.Integer(string='sequence')
    product_tmpl_id = fields.Many2one('product.template', string='Product Template', ondelete='cascade')

    _defaults = {
        'sequence': lambda *a: 10,
    }

    _sql_constraints = [
        ('code_uniq', 'unique(name)', 'Alternative code must be unique !'),
    ]

    # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
