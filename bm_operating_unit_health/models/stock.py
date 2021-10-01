# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
# [GCC 8.4.0]
# Embedded file name: /opt/odoo-10/addons-health/bm_operating_unit_health/models/stock.py
# Compiled at: 2019-02-09 09:22:44
from odoo import models, fields, api, _

class stock_location(models.Model):
    _inherit = 'stock.location'
    
    owner_user = fields.Many2one(comodel_name='res.users', string='Owner Login')
    unit_ids = fields.Many2many('unit.administration', 'unit_location_rel', 'location_id', 'unit_id', string='Units')

    @api.onchange('owner_user')
    def onchange_reason(self):
        self.partner_id = self.owner_user.partner_id.id