import xlsxwriter
import base64
from odoo import fields, models, api
from cStringIO import StringIO
from datetime import datetime
from pytz import timezone
import pytz

class WizardNextStep(models.TransientModel):
    _name = "wizard.next.step"

    queue_type_id = fields.Many2one('queue.type', 'Queue Type', required=False)
    is_valid = fields.Boolean('Is Valid', default=False)

    def confirm_next_step(self):
        unit_registration_id = self.env['unit.registration'].browse(self._context.get('active_id'))
        unit_registration_id.queue_trans_id.write({'type_id' : self.queue_type_id.id, 'state': 'draft'})        
        unit_registration_id.state = 'Unlock'