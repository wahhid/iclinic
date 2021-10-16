from odoo import models, fields, api, _
from odoo.exceptions import Warning
import logging

_logger = logging.getLogger(__name__)



class StockPackOperationLot(models.Model):
    _inherit = 'stock.pack.operation.lot'

    life_date = fields.Datetime("Expired Date", related="lot_id.life_date")

