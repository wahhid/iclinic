from odoo import models, fields, api, _

class operating_unit(models.Model):
    _inherit = 'operating.unit'

    unit_address = fields.Char(string='Address')