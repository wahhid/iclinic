from odoo import _, api, fields, models, tools


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    unit_administration_id = fields.Many2one('unit.administration','Unit Administration')
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', related='unit_administration_id.operating_unit_id')


