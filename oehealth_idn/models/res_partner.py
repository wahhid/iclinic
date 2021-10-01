# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
# [GCC 8.4.0]
# Embedded file name: D:\Workspaces\Odoo10\mod\Health\addons-custom\oehealth_idn\models\res_partner.py
# Compiled at: 2019-01-08 15:56:06
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DSDF, DEFAULT_SERVER_DATETIME_FORMAT

class res_partner_patient(models.Model):
    _inherit = 'res.partner'
    patient_member = fields.Selection([('Normal', 'Normal'),
     ('Employee', 'Employee'),
     ('Investor', 'Investor'),
     ('Executive Lounge', 'Executive Lounge'),
     ('Laguna', 'Laguna'),
     ('VIP', 'VIP'),
     ('VVIP', 'VVIP'),
     ('Student Member', 'Student Member')], 'Member Status')
    religion = fields.Selection([('Islam', 'Islam'),
     ('Katholik', 'Katholik'),
     ('Kristen', 'Kristen'),
     ('Hindu', 'Hindu'),
     ('Budha', 'Budha'),
     ('Konghuchu', 'Konghuchu'),
     ('Lainnya', '(Lainnya)')], 'Religion')
    is_blacklist = fields.Boolean('Blacklist ?')
    blacklist_reason = fields.Text('Blacklist Reason')
    place_birth = fields.Char('Place of Birth')
    identity = fields.Char('KTP / SIM')
    education = fields.Char('Education')
    nationality = fields.Char('Nationality')
    name = fields.Char(index=True)
    komplek = fields.Char('Komplek')
    npwp = fields.Char(string='NPWP', required=False)
    blok = fields.Char(string='Blok', required=False)
    nomor = fields.Char(string='Nomor', required=False)
    rt = fields.Char(string='RT', required=False)
    rw = fields.Char(string='RW', required=False)

    @api.depends('street', 'street2', 'city', 'state_id', 'country_id', 'blok', 'nomor', 'rt', 'rw', 'kelurahan_id', 'kecamatan_id')
    def _alamat_lengkap(self):
        for partner in self:
            lengkap = partner.street or ''
            lengkap += ' ' + (partner.street2 or '')
            if partner.blok:
                lengkap += ' Blok: ' + partner.blok + ', '
            if partner.nomor:
                lengkap += ' Nomor: ' + partner.nomor + ', '
            if partner.rt:
                lengkap += ' RT: ' + partner.rt
            if partner.rw:
                lengkap += ' RW: ' + partner.rw
            if partner.kelurahan_id:
                lengkap += ' Kel: ' + partner.kelurahan_id.name + ','
            if partner.kecamatan_id:
                lengkap += ' Kec: ' + partner.kecamatan_id.name
            if partner.kota_id:
                lengkap += '\n            ' + partner.kota_id.name + ','
            if partner.state_id:
                lengkap += ' ' + partner.state_id.name
            partner.alamat_lengkap = lengkap.upper()

    alamat_lengkap = fields.Char(string='Alamat Lengkap', required=False, compute='_alamat_lengkap')
    customer_type = fields.Selection([('Personal', 'Personal'), ('Company', 'Company'), ('Insurance', 'Insurance')], string='Customer Type', store=True)
    vendor_type = fields.Selection([('Medical', 'Medical'), ('Non-Medical', 'Non-Medical')], 'Vendor Type')

    @api.onchange('company_type')
    def onchange_customer_type(self):
        for row in self:
            if row.company_type == 'person':
                row.customer_type = 'Personal'
            elif row.company_type == 'company':
                row.customer_type = 'Company'