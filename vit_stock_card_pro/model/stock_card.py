# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Dec  8 2021, 21:08:43) 
# [GCC 8.4.0]
# Embedded file name: D:\Workspaces\Odoo10\mod\Health\addons-comcustom\vit_stock_card_pro\model\stock_card.py
# Compiled at: 2017-10-19 15:53:34
from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
SC_STATES = [
 ('draft', 'Draft'), ('open', 'Open'), ('done', 'Done')]

class stock_card(models.Model):
    _name = 'vit.stock_card'
    _rec_name = 'product_id'
    ref = fields.Char('Number', default='/')
    date_start = fields.Date('Date Start', required=True, default=lambda *a: time.strftime('%Y-%m-%d'))
    date_end = fields.Date('Date End', required=True, default=lambda *a: time.strftime('%Y-%m-%d'))
    location_id = fields.Many2one('stock.location', 'Location', required=True)
    product_id = fields.Many2one('product.product', 'Product', required=True)
    breakdown_sn = fields.Boolean('Per Serial Number?')
    lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number')
    expired_date = fields.Datetime(string='Expired Date', type='date', related='lot_id.life_date')
    line_ids = fields.One2many('vit.stock_card_line', 'stock_card_id', 'Details', ondelete='cascade')
    state = fields.Selection(SC_STATES, 'Status', readonly=True, required=True, default='draft')
    user_id = fields.Many2one('res.users', 'Created', default=lambda self: self.env.user)

    @api.multi
    def action_calculate(self):
        cr = self.env.cr
        stock_move = self.env['stock.move']
        stock_card_line = self.env['vit.stock_card_line']
        product = self.env['product.product']
        cr.execute('delete from vit_stock_card_line where stock_card_id=%s' % self.id)
        qty_start = 0.0
        qty_balance = 0.0
        qty_in = 0.0
        qty_out = 0.0
        product_uom = False
        lot_id = False
        if self.breakdown_sn:
            lot_id = self.lot_id
            sql2 = 'select move_id from stock_quant_move_rel qm join stock_quant q on qm.quant_id = q.id where q.lot_id = %s' % lot_id.id
        else:
            sql2 = 'select move_id from stock_quant_move_rel qm join stock_quant q on qm.quant_id = q.id where q.product_id = %s' % self.product_id.id
        cr.execute(sql2)
        res = cr.fetchall()
        move_ids = []
        if res and res[0] != None:
            for move in res:
                move_ids.append(move[0])

        if move_ids:
            move_string = '(' + ('').join([ str(x) for x in move_ids ]) + ')'
            sql = "select sum(product_uom_qty) from stock_move where product_id=%s and date < '%s' and location_dest_id=%s and id in %s and state='done'" % (
             self.product_id.id, self.date_start, self.location_id.id, move_string)
            cr.execute(sql)
            res = cr.fetchone()
            if res and res[0] != None:
                qty_start = res[0]
            sql = "select sum(product_uom_qty) from stock_move where product_id=%s and date < '%s' and location_id=%s and id in %s and state='done'" % (
             self.product_id.id, self.date_start, self.location_id.id, move_string)
            cr.execute(sql)
            res = cr.fetchone()
            if res and res[0] != None:
                qty_start = qty_start - res[0]
        prod = self.product_id
        product_uom = prod.uom_id
        data = {'stock_card_id': self.id, 
           'date': False, 
           'qty_start': False, 
           'qty_in': False, 
           'qty_out': False, 
           'qty_balance': qty_start, 
           'product_uom_id': product_uom.id}
        stock_card_line.create(data)
        sm_ids = stock_move.search([
         '|',
         (
          'location_dest_id', '=', self.location_id.id),
         (
          'location_id', '=', self.location_id.id),
         (
          'product_id', '=', self.product_id.id),
         (
          'date', '>=', self.date_start),
         (
          'date', '<=', self.date_end),
         ('state', '=', 'done'),
         (
          'id', 'in', move_ids)], order='date asc')
        for sm in sm_ids:
            qty_in = 0.0
            qty_out = 0.0
            if product_uom.id != sm.product_uom.id:
                factor = product_uom.factor / sm.product_uom.factor
            else:
                factor = 1.0
            if sm.location_dest_id == self.location_id:
                qty_in = sm.product_uom_qty * factor
            elif sm.location_id == self.location_id:
                qty_out = sm.product_uom_qty * factor
            qty_balance = qty_start + qty_in - qty_out
            name = sm.name if sm.name != prod.display_name else ''
            partner_name = sm.partner_id.name if sm.partner_id else ''
            notes = sm.picking_id.note or ''
            po_no = sm.group_id.name if sm.group_id else ''
            origin = sm.origin or ''
            finish_product = ''
            # if 'MO' in origin:
            #     mrp = self.env['mrp.production']
            #     mo_id = mrp.search([('name', '=', origin)])
            #     mo = mrp.browse(mo_id)
            #     finish_product = '%s:%s' % (mo[0].product_id.name, mo[0].batch_number) if mo else ''
            final_name = name
            name += ' ' + finish_product if finish_product else ''
            name += ' ' + partner_name if partner_name else ''
            name += ' ' + notes if notes else ''
            name += ' ' + origin if origin else ''
            data = {'stock_card_id': self.id, 
               'move_id': sm.id, 
               'picking_id': sm.picking_id.id, 
               'lot_id': self.find_lot_id(cr, sm.id), 
               'date': sm.date, 
               'qty_start': qty_start, 
               'qty_in': qty_in, 
               'qty_out': qty_out, 
               'qty_balance': qty_balance, 
               'product_uom_id': product_uom.id, 
               'name': final_name}
            stock_card_line.create(data)
            qty_start = qty_balance

        return

    def action_draft(self):
        return self.write({'state': SC_STATES[0][0]})

    def action_confirm(self):
        return self.write({'state': SC_STATES[1][0]})

    def action_done(self):
        return self.write({'state': SC_STATES[2][0]})

    @api.model
    def create(self, vals):
        vals['ref'] = self.env['ir.sequence'].next_by_code('vit.stock_card')
        new_id = super(stock_card, self).create(vals)
        return new_id

    def find_lot_id(self, cr, move_id):
        lot_id = False
        sql = 'select distinct(q.lot_id) from stock_quant_move_rel rel join stock_quant q on rel.quant_id=q.id where move_id=%s'
        cr.execute(sql, (move_id,))
        res = cr.fetchall()
        if res and res[0] != None:
            lot_id = res[0]
        return lot_id


class stock_card_line(models.Model):
    _name = 'vit.stock_card_line'
    name = fields.Char('Description')
    stock_card_id = fields.Many2one('vit.stock_card_id', 'Stock Card')
    move_id = fields.Many2one('stock.move', 'Stock Move')
    picking_id = fields.Many2one('stock.picking', 'Picking')
    lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number')
    date = fields.Date('Date')
    qty_start = fields.Float('Start')
    qty_in = fields.Float('Qty In')
    qty_out = fields.Float('Qty Out')
    qty_balance = fields.Float('Balance')
    product_uom_id = fields.Many2one('product.uom', 'UoM')