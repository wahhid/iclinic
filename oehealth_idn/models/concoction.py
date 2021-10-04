# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
# [GCC 8.4.0]
# Embedded file name: D:\Workspaces\Odoo10\mod\Health\addons-custom\oehealth_idn\models\concoction.py
# Compiled at: 2018-06-22 02:48:50
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime, math, odoo.addons.decimal_precision as dp

class sale_order_concoction(models.Model):
    _inherit = 'sale.order'
    concoction_ids = fields.One2many('medical.concoction', 'con_sale_id', copy=True, string='Concoction')

    @api.multi
    def action_confirm(self):
        res = super(sale_order_concoction, self).action_confirm()
        for line in self.concoction_ids:
            if line.state == 'draft':
                line.confirm_order()

        return res

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        res = super(sale_order_concoction, self).action_invoice_create(grouped=False, final=False)
        inv_line = self.env['account.invoice.line']
        for row in self:
            for line in row.concoction_ids:
                account = line.product_id.property_account_income_id or line.product_id.categ_id.property_account_income_categ_id
                if not account:
                    raise UserError(_('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') % (
                     line.product_id.name, line.product_id.id, line.product_id.categ_id.name))
                vals = {'invoice_id': res[0], 'name': line.product_id.name, 
                   'origin': line.con_sale_id.name, 
                   'account_id': account.id, 
                   'price_unit': line.price, 
                   'quantity': line.qty, 
                   'uom_id': line.product_uom.id, 
                   'product_id': line.product_id.id or False, 
                   'patient_id': line.con_sale_id.patient_id.id or False, 
                   'reg_id': line.con_sale_id.reg_id.id or False, 
                   'arrival_id': line.con_sale_id.arrival_id.id or False}
                inv_line.create(vals)

            return res


class medical_concoction(models.Model):
    _name = 'medical.concoction'
    _rec_name = 'product_id'
    con_sale_id = fields.Many2one(comodel_name='sale.order', string='Concoction Sale ID')
    prescription_id = fields.Many2one('oeh.medical.prescription', 'Prescription #')
    prescription_line_id = fields.Many2one('oeh.medical.health.center.pharmacy.line', 'Prescription Line #')
    product_id = fields.Many2one(comodel_name='product.product', string='Item', states={'done': [('readonly', True)]})
    is_concoction = fields.Boolean('Concoction', default=False, readonly=True)

    item_type = fields.Selection(related='product_id.item_type', string='Type')
    date = fields.Datetime(string='Date', default=datetime.datetime.now())
    doctor_id = fields.Many2one(comodel_name='oeh.medical.physician', string='Doctor', states={'done': [('readonly', True)]})
    qty = fields.Float(string='Quantity', states={'done': [('readonly', True)]})
    qty_unit = fields.Float(string='Quantity Unit', states={'done': [('readonly', True)]})
    product_uom = fields.Many2one(comodel_name='product.uom', string='UoM', states={'done': [('readonly', True)]})
    price = fields.Float(string='Price', compute='get_total_price')
    concoction_detail_ids = fields.One2many('medical.concoction.detail', 'concoction_id', copy=True, string='Concoction Detail', states={'done': [('readonly', True)]})
    state = fields.Selection([
     ('draft', 'Draft'),
     ('done', 'Done'),
     ('cancel', 'Cancelled')], string='Status', readonly=True, copy=False, index=True, default='draft')

    @api.onchange('product_id')
    def onchange_product_id(self):
        for row in self:
            row.product_uom = row.product_id.uom_id.id

    @api.depends('concoction_detail_ids')
    def get_total_price(self):
        for row in self:
            total = 0.0
            for line in row.concoction_detail_ids:
                subtotal = line.product_id.lst_price * line.total
                total += subtotal

            row.price = total

    @api.multi
    def confirm_order(self):
        move = self.env['stock.move']
        for data in self:
            for row in data.concoction_detail_ids:
                vals = {'product_id': row.product_id.id, 
                   'product_uom_qty': row.qty, 
                   'product_uom': row.uom_id.id, 
                   'name': row.product_id.name, 
                   'date_expected': datetime.datetime.now(), 
                   'origin': data.con_sale_id.name, 
                   'partner_id': data.con_sale_id.partner_id.id, 
                   'picking_partner_id': data.con_sale_id.partner_shipping_id.id, 
                   'location_id': data.con_sale_id.location_id.id, 
                   'location_dest_id': data.con_sale_id.partner_id.property_stock_customer.id}
                res = move.create(vals)
                res.action_done()

            data.state = 'done'


class medical_concoction_detail(models.Model):
    _name = 'medical.concoction.detail'
    _rec_name = 'product_id'
    concoction_id = fields.Many2one(comodel_name='medical.concoction', string='Concoction ID')
    product_id = fields.Many2one(comodel_name='product.product', string='Name')
    item_type = fields.Selection(related='product_id.item_type', string='Type')
    big_qty = fields.Float(string='Big Qty', digits=(16, 3))
    uom_po_id = fields.Many2one(related='product_id.uom_po_id', string='Big Unit')
    qty = fields.Float(string='Quantity', digits=(16, 3))
    uom_id = fields.Many2one(related='product_id.uom_id', string='Small Unit')
    zat_qty = fields.Float(string='Zat Aktif', digits=(16, 3))
    zat_uom = fields.Many2one(related='product_id.zat_uom', string='Zat Aktif Unit')
    total = fields.Float(string='Total Qty', compute='get_total')

    @api.onchange('product_id')
    def check_product_id(self):
        for row in self:
            if not row.concoction_id.product_id:
                raise UserError('Product Item not set. Please select one!')
            elif not row.concoction_id.qty:
                raise UserError('Quantity is zero. Please set quantity!')

    @api.depends('qty')
    def get_total(self):
        for row in self:
            total = math.ceil(row.concoction_id.qty * row.qty)
            row.total = total

    @api.onchange('big_qty')
    def onchange_big_qty(self):
        for row in self:
            if row.uom_id:
                qty = row.uom_po_id._compute_quantity(row.big_qty, row.uom_id)
                row.qty = qty
            if row.zat_uom:
                zat = row.uom_po_id._compute_quantity(row.big_qty, row.zat_uom)
                row.zat_qty = zat

    @api.onchange('qty')
    def onchange_qty(self):
        for row in self:
            if row.uom_po_id:
                big = row.uom_id._compute_quantity(row.qty, row.uom_po_id)
                row.big_qty = big
            if row.zat_uom:
                zat = row.uom_id._compute_quantity(row.qty, row.zat_uom)
                row.zat_qty = zat

    @api.onchange('zat_qty')
    def onchange_zat_qty(self):
        for row in self:
            if row.uom_po_id:
                big = row.zat_uom._compute_quantity(row.zat_qty, row.uom_po_id)
                row.big_qty = big
            if row.uom_id:
                qty = row.zat_uom._compute_quantity(row.zat_qty, row.uom_id)
                row.qty = qty