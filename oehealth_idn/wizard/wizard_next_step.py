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
    is_current_unit = fields.Boolean('Is Current Unit', default=False)
    is_current_lab = fields.Boolean('Is Current Lab', default=False)
    is_current_pharmacy = fields.Boolean('Is Current Pharmacy', default=False)

    def confirm_next_step(self):
        if self.is_start:
            walkin_id = self.env['oeh.medical.appointment.register.walkin'].browse(self._context.get('active_id'))
            walkin_id.queue_trans_id.write({'type_id' : self.queue_type_id.id, 'state': 'draft'})        
            walkin_id.state = 'Scheduled'
        else:
            if self.queue_type_id.is_unit:
                if self.is_current_unit:
                    unit_registration_id = self.env['unit.registration'].browse(self._context.get('active_id'))
                    unit_registration_id.queue_trans_id.write({'type_id' : self.queue_type_id.id, 'state': 'draft'})        
                    unit_registration_id.state = 'Unlock'

                if self.is_current_lab:
                    lab_test_id = self.env['oeh.medical.lab.test'].browse(self._context.get('active_id'))
                    lab_test_id.queue_trans_id.write({'type_id' : self.queue_type_id.id, 'state': 'draft'})        
                    #lab_test_id.state = 'Unlock'
                
                if self.is_current_pharmacy:
                    pharmacy_order_id = self.env['oeh.medical.health.center.pharmacy.line'].browse(self._context.get('active_id'))
                    pharmacy_order_id.queue_trans_id.write({'type_id' : self.queue_type_id.id, 'state': 'draft'})        


            elif self.queue_type_id.is_lab:
                if self.is_current_unit:
                    unit_registration_id = self.env['unit.registration'].browse(self._context.get('active_id'))
                    unit_registration_id.queue_trans_id.write({'type_id' : self.queue_type_id.id, 'state': 'draft'})        
                
                if self.is_current_lab:
                    lab_test_id = self.env['oeh.medical.lab.test'].browse(self._context.get('active_id'))
                    lab_test_id.queue_trans_id.write({'type_id' : self.queue_type_id.id, 'state': 'draft'})        
                    #lab_test_id.state = 'Unlock'

                if self.is_current_pharmacy:
                    pharmacy_order_id = self.env['oeh.medical.health.center.pharmacy.line'].browse(self._context.get('active_id'))
                    pharmacy_order_id.queue_trans_id.write({'type_id' : self.queue_type_id.id, 'state': 'draft'})        


            elif self.is_current_pharmacy:
                if self.is_current_unit:
                    unit_registration_id = self.env['unit.registration'].browse(self._context.get('active_id'))
                    unit_registration_id.queue_trans_id.write({'type_id' : self.queue_type_id.id, 'state': 'draft'})        
                
                if self.is_current_lab:
                    lab_test_id = self.env['oeh.medical.lab.test'].browse(self._context.get('active_id'))
                    lab_test_id.queue_trans_id.write({'type_id' : self.queue_type_id.id, 'state': 'draft'})        
                    #lab_test_id.state = 'Unlock'

                if self.is_current_pharmacy:
                    pharmacy_order_id = self.env['oeh.medical.health.center.pharmacy.line'].browse(self._context.get('active_id'))
                    pharmacy_order_id.queue_trans_id.write({'type_id' : self.queue_type_id.id, 'state': 'draft'})        

                
            else:
                pass

    def confirm_finish(self):
        if self.queue_type_id.is_unit:
            if self.is_current_unit:
                unit_registration_id = self.env['unit.registration'].browse(self._context.get('active_id'))
                unit_registration_id.queue_trans_id.write({'type_id' : self.queue_type_id.id, 'state': 'draft'})        
                unit_registration_id.state = 'Unlock'
            if self.is_current_lab:
                lab_test_id = self.env['oeh.medical.lab.test'].browse(self._context.get('active_id'))
                lab_test_id.queue_trans_id.write({'type_id' : self.queue_type_id.id, 'state': 'draft'})        
                #lab_test_id.state = 'Unlock'

        elif self.queue_type_id.is_lab:
            if self.is_current_unit:
                unit_registration_id = self.env['unit.registration'].browse(self._context.get('active_id'))
                unit_registration_id.queue_trans_id.write({'type_id' : self.queue_type_id.id, 'state': 'draft'})        
            
            if self.is_current_lab:
                lab_test_id = self.env['oeh.medical.lab.test'].browse(self._context.get('active_id'))
                lab_test_id.queue_trans_id.write({'type_id' : self.queue_type_id.id, 'state': 'draft'})        
                #lab_test_id.state = 'Unlock'
            

