from odoo import models, fields, api, _

class operating_unit(models.Model):
    _inherit = 'operating.unit'

    unit_address = fields.Char(string='Address')
    izin_klinik = fields.Char(string='No. Izin Klinik')
    izin_apotik = fields.Char(string='No. Izin Apotik')