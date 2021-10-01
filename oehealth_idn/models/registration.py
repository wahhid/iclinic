# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
# [GCC 8.4.0]
# Embedded file name: D:\Workspaces\Odoo10\mod\Health\addons-custom\oehealth_idn\models\registration.py
# Compiled at: 2018-12-12 15:45:33
from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
import datetime, requests, json

class register_walkin(models.Model):
    _inherit = 'oeh.medical.appointment.register.walkin'
    PAYMENT_TYPE = [
     ('Personal', 'Personal'),
     ('Corporate', 'Corporate'),
     ('Insurance', 'Insurance')]
    WALKIN_STATUS = [
     ('Draft', 'Draft'),
     ('Scheduled', 'Scheduled'),
     ('Completed', 'Completed'),
     ('Invoiced', 'Invoiced'),
     ('Cancelled', 'Cancelled')]

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            tit = '%s / %s' % (record.name, record.patient.name)
            res.append((record.id, tit))

        return res

    clinic_ids = fields.One2many(comodel_name='unit.registration', inverse_name='clinic_walkin_id', string='Out-Patient Registration', readonly=True, states={'Scheduled': [('readonly', False)]}, track_visibility='onchange')
    unit_ids = fields.One2many(comodel_name='unit.registration', inverse_name='unit_walkin_id', string='In-Patient Registration', readonly=True, states={'Scheduled': [('readonly', False)]}, track_visibility='onchange')
    emergency_ids = fields.One2many(comodel_name='unit.registration', inverse_name='emergency_walkin_id', string='Emergency Registration', readonly=True, states={'Scheduled': [('readonly', False)]}, track_visibility='onchange')
    support_ids = fields.One2many(comodel_name='unit.registration', inverse_name='support_walkin_id', string='Medical Support Registration', readonly=True, states={'Scheduled': [('readonly', False)]}, track_visibility='onchange')
    payment = fields.Selection(PAYMENT_TYPE, string='Payment Guarantor', default='Personal', readonly=True, states={'Scheduled': [('readonly', False)]}, track_visibility='onchange')
    company = fields.Many2one(comodel_name='res.partner', string='Company', readonly=True, states={'Scheduled': [('readonly', False)]}, track_visibility='onchange')
    insurance = fields.Many2one(comodel_name='medical.insurance', string='Insurance', readonly=True, states={'Scheduled': [('readonly', False)]}, track_visibility='onchange')
    unit = fields.Many2one(comodel_name='unit.administration', string='Unit', track_visibility='onchange')
    admission_reason = fields.Many2one('oeh.medical.pathology', string='Reason for Admission', help='Reason for Admission', required=False, readonly=True, states={'Scheduled': [('readonly', False)]}, track_visibility='onchange')
    have_register = fields.Boolean(string='Have Register ?')
    is_blacklist = fields.Boolean(related='patient.is_blacklist')
    state = fields.Selection(WALKIN_STATUS, string='State', readonly=True, states={'Scheduled': [('readonly', False)]}, default=lambda *a: 'Draft')

    @api.model
    def create(self, vals):
        vals['state'] = 'Scheduled'
        count = self.env['oeh.medical.appointment.register.walkin'].search([('patient', '=', vals['patient']), ('state', '=', 'Scheduled')])
        if count:
            raise Warning('The patient already has an active registration! \n Please Check Arrival ID # ' + count.name)
        return super(register_walkin, self).create(vals)

    @api.onchange('patient', 'dob')
    def check_registration(self):
        count = self.env['oeh.medical.appointment.register.walkin'].search([('patient', '=', self.patient.id), ('state', '=', 'Scheduled')])
        self.insurance = self.patient.current_insurance.id
        if count:
            raise Warning('The patient already has an active registration! \n Please Check Arrival ID # ' + count.name)

    @api.multi
    def set_to_completed(self):
        if not self.clinic_ids and not self.unit_ids and not self.emergency_ids and not self.support_ids:
            raise UserError(_('Completed Failed! \n Registration Line empty !'))
        else:
            for line in self.clinic_ids:
                if line.state in 'Unlock':
                    raise UserError(_('Out-Patient Care! \n Reg ID # ' + line.name + ' must be lock first !'))

            for line in self.unit_ids:
                if line.state in 'Unlock':
                    raise UserError(_('In-Patient Care! \n Reg ID # ' + line.name + ' must be lock first !'))

            for line in self.emergency_ids:
                if line.state in 'Unlock':
                    raise UserError(_('Emergency Care! \n Reg ID # ' + line.name + ' must be lock first !'))

            for line in self.support_ids:
                if line.state in 'Unlock':
                    raise UserError(_('Medical Support! \n Reg ID # ' + line.name + ' must be lock first !'))

            return self.write({'state': 'Completed'})

    @api.multi
    def set_to_cancelled(self):
        if not self.clinic_ids and not self.unit_ids and not self.emergency_ids and not self.support_ids:
            return self.write({'state': 'Cancelled'})
        raise UserError(_('Cancelled Failed! \n Registration not empty !'))

    @api.multi
    def unlink(self):
        if self.clinic_ids or self.unit_ids or self.emergency_ids or self.support_ids:
            raise UserError(_('Deleted Failed! \n Registration not empty !'))
        return super(register_walkin, self).unlink()

    @api.multi
    def print_patient_stiker(self):
        return self.patient.print_patient_stiker()


    @api.multi
    def onchange_patient(self, patient):
        if patient:
            patient = self.env['oeh.medical.patient'].browse(patient)
            if patient.is_employee:
                return {
                    'value': {
                        'dob': patient.dob, 
                        'sex': patient.sex, 
                        'marital_status': 
                        patient.marital_status, 
                        'blood_type': patient.blood_type, 
                        'rh': patient.rh
                    },
                    'warning': {
                        'title': _('Warning'),
                        'message': _('This Pasien is employee')
                    }
                }
            elif patient.is_have_parent:
                return {
                    'value': {
                        'dob': patient.dob, 
                        'sex': patient.sex, 
                        'marital_status': 
                        patient.marital_status, 
                        'blood_type': patient.blood_type, 
                        'rh': patient.rh
                    },
                    'warning': {
                        'title': _('Warning'),
                        'message': _('This Pasien have relation with employee')
                    }
                }
            else:
                return {'value': {'dob': patient.dob, 'sex': patient.sex, 'marital_status': patient.marital_status, 'blood_type': patient.blood_type, 'rh': patient.rh}}
        return {}
