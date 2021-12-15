from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning


class QueueKiosk(models.Model):
    _inherit = 'queue.kiosk'
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit')


class QueueDisplay(models.Model):
    _inherit = 'queue.display'
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit')


class QueueType(models.Model):
    _inherit = 'queue.type'
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit')
    unit_administration_id = fields.Many2one('unit.administration', 'Unit Administration')

class QueuePickup(models.Model):
    _inherit = 'queue.pickup'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit')

class QueuePickupLog(models.Model):
    _inherit = 'queue.pickup.log'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit')

class QueueTrans(models.Model):
    _inherit = 'queue.trans'
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit')

