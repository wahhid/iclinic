import logging
from datetime import timedelta
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.http import request
from datetime import datetime, date

_logger = logging.getLogger(__name__)

class owlexa_batch(models.Model):
    _name = 'owlexa.batch'  

    @api.multi
    def trans_process_document(self):
        for account_invoice_id in self.account_invoice_ids:
            _logger.info(account_invoice_id.number)

    name = fields.Char('Name', size=100, required=True)
    trans_date = fields.Date('Date', default=date.today())
    account_invoice_ids = fields.Many2many('account.invoice', 'owlexa_batch_account_invoice_rel',  'account_invoice_id', 'owlexa_batch_id', 'Invoices')



