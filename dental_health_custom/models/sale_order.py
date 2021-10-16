# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class sale_order(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        for row in self:
            if row.reg_id:
                if row.reg_id.state not in ('Lock', 'Check-Out', 'Done'):
                    query = _("UPDATE unit_registration SET STATE='Lock' WHERE id=%s") % (str(row.reg_id.id))
                    self.env.cr.execute(query)
        res = super(sale_order, self).action_confirm()
        return res
