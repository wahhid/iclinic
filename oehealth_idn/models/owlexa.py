import logging
from datetime import timedelta
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.http import request
from datetime import datetime, date
import requests
import json

_logger = logging.getLogger(__name__)

AVAILABLESTATES = [
    ('draft','Draft'),
    ('generate','Generate Report'),
    ('sync','Sync To Owlexa'),
    ('upload','Upload Document'),
    ('batch','Create Batch'),
    ('done','Close')
]
class owlexa_batch(models.Model):
    _name = 'owlexa.batch'  
    _inherit = ['mail.thread']
    _description = "Owlexa Batch"


    @api.multi
    def trans_generate_document(self):
        for account_invoice_id in self.account_invoice_ids:
            _logger.info(account_invoice_id.number)
            account_invoice_id.with_context({'batch_id': self.id}).generate_insurance_report_file()
        self.state = 'generate'

    @api.multi
    def trans_sync_transaction(self):
        for account_invoice_id in self.account_invoice_ids:
            _logger.info(account_invoice_id.number)
            account_invoice_id.sync_to_owlexa()
        self.state = 'sync'

    @api.multi
    def trans_upload_document(self):
        for account_invoice_id in self.account_invoice_ids:
            _logger.info(account_invoice_id.number)
            account_invoice_id.upload_document_to_owlexa()
        self.state = 'upload'

    @api.multi
    def trans_create_batch(self):
        account_numbers = []
        amount_paid  = 0
        for account_invoice_id in self.account_invoice_ids:
           _logger.info(account_invoice_id.number)
           account_numbers.append(account_invoice_id.number)
           amount_paid = amount_paid + account_invoice_id.amount_total_temp

        data = {
            "totalTransaction" : self.total_count,
            "invoiceNumber" : self.name,
            "invoiceDate" : self.trans_date,
            "amountPaid" : amount_paid,
            "providerTransactionNumberList" : account_numbers
        }

        _logger.info(data)

        headers = {
                'API-Key': '8HCmYbU+phImFJXgg1hHjpd6HBQFekEUvsn+TGoBDkc=',
                'Content-Type': 'application/json'
                }
        base_url = 'https://test.owlexa.com/owlexa-api/invoice/v1/create-document-batch'
        try:
            # data = {
            #     "claimNumber" : self.claim_number,
            #     "cardNumber": "1000620030002010",
            #     "paidToProviderAmount": self.amount_total_temp,
            #     "providerTransactionNumber": self.number
            # }
            _logger.info(data)
            req = requests.post(base_url, headers=headers ,data=json.dumps(data))
            _logger.info(req.text)
            response_json = req.json()
            if req.status_code != 200:
                body = """
                    Create Batch Error <br/>
                    Code : {}
                """.format(response_json['code'])
                self.message_post(body=body)
                _logger.info("Error")
            else:
                
                body = """
                    Create Batch <br/>
                    <ul>
                        <li>Code : {}</li>
                        <li>Data : {}</li>
                        <li>Message : {}</li>
                        <li>Status : {}</li>
                        <li>Total Data : {}</li>
                        <li>Trans ID : {}</li>
                    </ul>
                """.format(response_json['code'], response_json['data'], response_json['message'], response_json['status'], response_json['totalData'], response_json['transactionId'])
                self.message_post(body=body)
                if response_json['code'] == 200:
                    _logger.info('Success')
                if response_json['code'] == 400:
                    _logger.info('Failed')
                if response_json['code'] == 401:
                    _logger.info('Failed')
           
        except Exception as err:
            _logger.error(err)  

        #for account_invoice_id in self.account_invoice_ids:
        #    _logger.info(account_invoice_id.number)
        #    account_invoice_id.generate_insurance_report_file()
    
    

    @api.depends('account_invoice_ids')
    def get_invoice_total_amount(self):
        for row in self:
            """
            Compute the total amounts of the Prescription lines.
            """
            val = 0.0
            for account_invoice_id in row.account_invoice_ids:
                val += account_invoice_id.amount_total
                
            row.total_amount = val
            #order.update({'amount_total': val})

    @api.depends('account_invoice_ids')
    def get_invoice_total_count(self):
        for row in self:                
            row.total_count = len(row.account_invoice_ids)
            #order.update({'amount_total': val})

    name = fields.Char('Name', size=100, required=True)
    trans_date = fields.Date('Date', default=date.today())
    partner_id = fields.Many2one('res.partner','Partner', required=True)
    total_count = fields.Integer('Total Count', compute="get_invoice_total_count", readonly=True)
    total_amount = fields.Float('Total Amount', compute="get_invoice_total_amount", readonly=True)
    account_invoice_ids = fields.Many2many('account.invoice', 'owlexa_batch_account_invoice_rel',  'account_invoice_id', 'owlexa_batch_id', 'Invoices')
    state = fields.Selection(AVAILABLESTATES, 'Status', readonly="1", default="draft")


