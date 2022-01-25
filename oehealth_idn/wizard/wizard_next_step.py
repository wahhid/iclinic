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
    is_start = fields.Boolean('Is Start', default=False)

    def confirm_next_step(self):
        if self.is_start:
            walkin_id = self.env['oeh.medical.appointment.register.walkin'].browse(self._context.get('active_id'))
            walkin_id.queue_trans_id.write({'type_id' : self.queue_type_id.id, 'state': 'draft'})        
            walkin_id.state = 'Scheduled'
        else:
            if self.queue_type_id.is_unit:
                unit_registration_id = self.env['unit.registration'].browse(self._context.get('active_id'))
                unit_registration_id.queue_trans_id.write({'type_id' : self.queue_type_id.id, 'state': 'draft'})        
                unit_registration_id.state = 'Unlock'
            elif self.queue_type_id.is_lab:
                lab_test_id = self.env['oeh.medical.lab.test'].browse(self._context.get('active_id'))
                lab_test_id.queue_trans_id.write({'type_id' : self.queue_type_id.id, 'state': 'draft'})        
                lab_test_id.state = 'Unlock'
            else:
                pass
            

