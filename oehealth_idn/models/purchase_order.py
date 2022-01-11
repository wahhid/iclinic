from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, AccessError
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def _add_supplier_to_product(self):
        # Add the partner in the supplier list of the product if the supplier is not registered for
        # this product. We limit to 10 the number of suppliers for a product to avoid the mess that
        # could be caused for some generic products ("Miscellaneous").
        super(PurchaseOrder,self)._add_supplier_to_product()
        _logger.info("Update Standard Price")
        for line in self.order_line:
            partner = self.partner_id if not self.partner_id.parent_id else self.partner_id.parent_id
            _logger.info(partner.name)
            currency = partner.property_purchase_currency_id or self.env.user.company_id.currency_id
            price = self.currency_id.compute(line.price_unit, currency)
            product_id = line.product_id
            if product_id.standard_price < price:
                _logger.info(product_id.name)
                _logger.info(price)
                product_id.standard_price = price
