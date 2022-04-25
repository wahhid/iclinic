# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
# [GCC 8.4.0]
# Embedded file name: D:\Workspaces\Odoo10\mod\Health\addons-custom\oehealth_idn\models\account_invoice.py
# Compiled at: 2019-01-09 17:38:07
from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning, ValidationError
import base64
import PyPDF2
from io import StringIO, BytesIO
import requests
import json
import logging
import uuid

_logger = logging.getLogger(__name__)



class account_invoice(models.Model):
    _inherit = 'account.invoice'

    def generate_insurance_report_file(self):
        _logger.info("Generate Insurance Report for " + self.number)
        pdfWriter = PyPDF2.PdfFileWriter()

        if self.is_has_owlexa_invoice:
            context=self.env.context
            _logger.info(context.get('batch_id'))
            report_name = "oehealth_idn.report_invoice_batch_owlexa"
            owlexa_report = self.env['report'].sudo().get_pdf([context.get('batch_id')], report_name)
            _logger.info(type(owlexa_report))
            owlexa_file = BytesIO()
            owlexa_file.write(owlexa_report)
            _logger.info(type(owlexa_file))
            pdfReader = PyPDF2.PdfFileReader(owlexa_file)
            # Loop through all the pagenumbers for the first document
            for pageNum in range(pdfReader.numPages):
                pageObj = pdfReader.getPage(pageNum)
                pdfWriter.addPage(pageObj)


        report_name = "oehealth_idn.report_formulir_rawat_jalan_owlexa"
        owlexa_report = self.env['report'].sudo().get_pdf([self.arrival_id.id], report_name)
        _logger.info(type(owlexa_report))
        owlexa_file = BytesIO()
        owlexa_file.write(owlexa_report)
        _logger.info(type(owlexa_file))
        pdf1Reader = PyPDF2.PdfFileReader(owlexa_file)
        # Loop through all the pagenumbers for the first document
        for pageNum in range(pdf1Reader.numPages):
            pageObj = pdf1Reader.getPage(pageNum)
            pdfWriter.addPage(pageObj)
       
        report_name = "account.report_invoice"
        invoice_report = self.env['report'].sudo().get_pdf([self.id], report_name)
        invoice_file = BytesIO()
        invoice_file.write(invoice_report)
        pdf2Reader = PyPDF2.PdfFileReader(invoice_file)

        # Loop through all the pagenumbers for the second document
        for pageNum in range(pdf2Reader.numPages):
            pageObj = pdf2Reader.getPage(pageNum)
            pdfWriter.addPage(pageObj)

        for prescription_id in self.arrival_id.prescription_ids:
            _logger.info(self.arrival_id.prescription_ids)
            report_name = "oehealth_idn.report_resep"
            #prescription_ids = [x.id for x in self.arrival_id.prescription_ids]
            resep_report = self.env['report'].sudo().get_pdf([prescription_id.id], report_name)
            resep_file = BytesIO()
            resep_file.write(resep_report)
            pdf3Reader = PyPDF2.PdfFileReader(resep_file)

            # Loop through all the pagenumbers for the second document
            for pageNum in range(pdf3Reader.numPages):
                pageObj = pdf3Reader.getPage(pageNum)
                pdfWriter.addPage(pageObj)
        
        #Lab Report
        for lab_test_id in self.arrival_id.lab_test_ids:
            report_name = "oehealth.report_oeh_medical_patient_labtest"
            lab_report = self.env['report'].sudo().get_pdf([lab_test_id.id], report_name)
            lab_file = BytesIO()
            lab_file.write(lab_report)
            pdf4Reader = PyPDF2.PdfFileReader(lab_file)

            # Loop through all the pagenumbers for the second document
            for pageNum in range(pdf4Reader.numPages):
                pageObj = pdf4Reader.getPage(pageNum)
                pdfWriter.addPage(pageObj)
                
        #Imaging Report
        #oehealth_extra_addons.report_oeh_medical_patient_imaging
        
        output_file = BytesIO()
        pdfWriter.write(output_file)
        self.invoice_pdf_file = base64.encodestring(output_file.getvalue())
        self.is_document_ready = True

    def sync_to_owlexa(self):
        _logger.info("Sync To Owlexa")
       
        headers = {
        'API-Key': '8HCmYbU+phImFJXgg1hHjpd6HBQFekEUvsn+TGoBDkc=',
        'Content-Type': 'application/json'
        }
        base_url = 'https://test.owlexa.com/owlexa-api/invoice/v1/sync-transaction'
        try:
            data = {
                "claimNumber" : self.claim_number,
                "cardNumber": "1000620030002010",
                "paidToProviderAmount": self.amount_total_temp,
                "providerTransactionNumber": self.number
            }
            _logger.info(data)
            req = requests.post(base_url, headers=headers ,data=json.dumps(data))
            _logger.info(req.text)
            response_json = req.json()
            if req.status_code != 200:
                body = """
                    Sync To Owlexa <br/>
                    Code : {}
                """.format(response_json['code'])
                self.message_post(body=body)
                _logger.info("Error")
            else:
                
                body = """
                    Sync To Owlexa <br/>
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
                    self.is_sync = True
                    _logger.info('Success')
                if response_json['code'] == 400:
                    _logger.info('Failed')
                if response_json['code'] == 401:
                    _logger.info('Failed')
           
        except Exception as err:
            _logger.error(err)  
    
    def upload_document_to_owlexa(self):
        _logger.info("Upload Document To Owlexa")
       
        headers = {
            'API-Key': '8HCmYbU+phImFJXgg1hHjpd6HBQFekEUvsn+TGoBDkc='
        }

        base_url = 'https://test.owlexa.com/owlexa-api/invoice/v1/upload-document'
        try:
 

            #file_content=base64.b64decode(self.invoice_pdf_file)
            # filename = "/tmp/" + str(uuid.uuid4())
            # with open(filename, 'wb') as file_to_save:
            #     decoded_data = base64.b64decode(self.invoice_pdf_file)
            #     file_to_save.write(decoded_data)
            
            # file_to_read = open(filename,'rb')


           #owlexa_file.write(file_content)

           

            file_content = base64.b64decode(self.invoice_pdf_file)
            filename = "/tmp/" + str(uuid.uuid4())
            _logger.info(filename)
            with open(filename, 'wb') as file_to_save:
                file_to_save.write(file_content)
            
            
            # multipart_form_data = {
            #     'file': ('file',('INV-00001.pdf',open(filename,'rb'),'application/pdf')),
            #     'includeInvoice': (None, 'true'),
            #     'providerTransactionNumber': (None, 'INV-00001')
            # }
            
            if self.is_has_owlexa_invoice:
                data={
                    'includeInvoice': 'true',
                    'providerTransactionNumber': self.number
                }
            else:
                data={
                    'includeInvoice': 'false',
                    'providerTransactionNumber': self.number
                }

            files=[
                ('file',(self.number + '.pdf',open(filename,'rb'),'application/pdf'))
            ]



            req = requests.post( base_url, headers=headers, data=data, files=files)
            response_json = req.json()
            if req.status_code != 200:
                body = """
                    Upload Document to Owlexa <br/>
                    Code : {}
                """.format(response_json['code'])
                self.message_post(body=body)
                _logger.info("Error")
            else:
                body = """
                    Upload Document To Owlexa <br/>
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
                    self.is_upload = True
                    _logger.info('Success')
                if response_json['code'] == 400:
                    _logger.info('Failed')
                if response_json['code'] == 401:
                    _logger.info('Failed')
           
        except Exception as err:
            _logger.error(err)  

    def check_document_status(self):
        _logger.info("Check Document Status")
       
        headers = {
            'Content-Type': 'application/json',
            'API-Key': '8HCmYbU+phImFJXgg1hHjpd6HBQFekEUvsn+TGoBDkc='
        }

        base_url = 'https://test.owlexa.com/owlexa-api/invoice/v1/check-document'
        try:
           
            data={
                'providerTransactionNumber': 'INV-00001'
            }

            req = requests.post( base_url, headers=headers, data=json.dumps(data))
            response_json = req.json()
            if req.status_code != 200:
                body = """
                    Check Document Status <br/>
                    Code : {}
                """.format(response_json['code'])
                self.message_post(body=body)
                _logger.info("Error")
            else:
                body = """
                    Check Document Status <br/>
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


    arrival_id = fields.Many2one(comodel_name='oeh.medical.appointment.register.walkin', string='Arrival ID')
    reg_id = fields.Many2one(comodel_name='unit.registration', string='Reg ID')
    medical_record = fields.Char(string='Medical Record', related='patient.identification_code')
    amount_pay = fields.Float(string='Amount Pay')
    amount_change = fields.Float(string='Change', compute='get_change')
    
    insurance_type_id = fields.Many2one('medical.insurance.type', 'Insurance Type')
    claim_number = fields.Char('Claim Number', size=100)
    amount_total_temp = fields.Float('Total Amount Temp')
    invoice_pdf_file = fields.Binary("Invoice PDF File", readonly=True)
    is_document_ready = fields.Boolean('Document Ready', default=False, readonly=True)
    is_sync = fields.Boolean("Is Sync", default=False, readonly=True)
    is_upload = fields.Boolean('Is Upload', default=False, readonly=True)
    is_has_owlexa_invoice = fields.Boolean("Has Owlexa Invoice", default=False)


    @api.depends('amount_pay')
    def get_change(self):
        for row in self:
            if row.amount_pay and row.residual:
                row.amount_change = row.amount_pay - row.residual
            else:
                row.amount_change = row.amount_pay - row.amount_total

    @api.multi
    def action_invoice_paid(self):
        to_pay_invoices = self.filtered(lambda inv: inv.state != 'paid')
        if to_pay_invoices.filtered(lambda inv: inv.state != 'open'):
            raise UserError(_('Invoice must be validated in order to set it to register payment.'))
        if to_pay_invoices.filtered(lambda inv: not inv.reconciled):
            raise UserError(_('You cannot pay an invoice which is partially paid. You need to reconcile payment entries first.'))
        if self.arrival_id:
            reg = self.env['oeh.medical.appointment.register.walkin'].browse(self.arrival_id.id)
            reg.write({'state': 'Completed'})
        return to_pay_invoices.write({'state': 'paid'})

    @api.multi
    def admin_fee(self):
        inv_line = self.env['account.invoice.line']
        inpatient = False
        for line in self.invoice_line_ids:
            if line.reg_id.type == 'In-Patient':
                inpatient = True
                arrival_id = line.arrival_id
                reg_id = line.reg_id

        if inpatient:
            product = self.env['product.product'].search([('admin_fee', '!=', False)])
            if product:
                for p in product:
                    inv_line.search([('invoice_id', '=', self.id), ('product_id', '=', p.id)]).unlink()
                    admin_fee_percent = 1
                    max_admin_fee = 0.0
                    ins = self.env['medical.insurance.type'].search([('partner_id', '=', self.partner_id.id)], limit=1)
                    if ins:
                        admin_fee_percent = ins.admin_fee
                        max_admin_fee = ins.max_admin_fee
                    else:
                        prv = self.env['medical.insurance.type'].search([('name', '=', 'Personal')], limit=1)
                        if prv:
                            admin_fee_percent = prv.admin_fee
                            max_admin_fee = prv.max_admin_fee
                        else:
                            raise UserError('Medical Insurance Type "Personal" Not Found!')
                            
                    admin_fee_value = self.amount_total * admin_fee_percent / 100
                    if max_admin_fee and admin_fee_value >= max_admin_fee:
                        admin_fee_value = max_admin_fee
                    else:
                        admin_fee_value = admin_fee_value
                    vals = {'invoice_id': self.id, 
                       'arrival_id': arrival_id.id, 
                       'reg_id': reg_id.id, 
                       'product_id': p.id, 
                       'name': p.name + ' ' + str(int(admin_fee_percent)) + '%', 
                       'account_id': p.property_account_income_id.id or p.categ_id.property_account_income_categ_id.id, 
                       'quantity': 1, 
                       'uom_id': p.uom_id.id, 
                       'price_unit': admin_fee_value}
                    adm_id = inv_line.create(vals)

            else:
                raise Warning('Product Administration Fee Label Not Found!')


class account_invoice_line(models.Model):
    _inherit = 'account.invoice.line'

    arrival_id = fields.Many2one(comodel_name='oeh.medical.appointment.register.walkin', string='Arrival ID')
    reg_id = fields.Many2one(comodel_name='unit.registration', string='Reg ID')
    patient_id = fields.Many2one(comodel_name='oeh.medical.patient', string='Patient')


class account_payment(models.Model):
    _inherit = 'account.payment'
    amount_pay = fields.Float(string='Amount Pay')
    amount_change = fields.Float(string='Change', compute='get_change')

    @api.depends('amount_pay', 'amount')
    def get_change(self):
        for row in self:
            if row.amount_pay:
                row.amount_change = row.amount_pay - row.amount
            if row.amount_change < 0:
                raise Warning('Amount Pay less than Payment Amount, Please Change Payment Amount!')