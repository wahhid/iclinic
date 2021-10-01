# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
# [GCC 8.4.0]
# Embedded file name: D:\Workspaces\Odoo10\mod\Health\addons-custom\oehealth_idn\models\appointment.py
# Compiled at: 2019-02-20 06:41:56
import datetime
from datetime import timedelta
import logging, pytz
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.translate import _
_logger = logging.getLogger(__name__)

class oeh_medical_appointment(models.Model):
    _inherit = 'oeh.medical.appointment'
    APPOINTMENT_STATUS = [
     ('Cancel', 'Cancel'),
     ('Scheduled', 'Scheduled'),
     ('Completed', 'Completed'),
     ('Visited', 'Visited'),
     ('Invoiced', 'Invoiced')]
    PATIENT_STATUS = [
     ('Out-Patient', 'Out-Patient'),
     ('In-Patient', 'In-Patient'),
     ('Emergency', 'Emergency'),
     ('Medical Support', 'Medical Support')]

    @api.multi
    def _get_appointment_end(self):
        for apm in self:
            end_date = False
            end_date = datetime.datetime.strptime(apm.appointment_date, '%Y-%m-%d %H:%M:%S') + timedelta(hours=apm.duration)
            apm.appointment_end = end_date

        return True

    unit = fields.Many2one(comodel_name='unit.administration', string='Unit', readonly=True, states={'Scheduled': [('readonly', False)]})
    patient_status = fields.Selection(PATIENT_STATUS, string='Patient Status', readonly=True, states={'Scheduled': [('readonly', False)]}, default=lambda *a: 'Out-Patient')
    duration = fields.Float(string='Duration (Hours)', readonly=True, states={'Scheduled': [('readonly', False)]}, default=lambda *a: 1)
    appointment_end = fields.Datetime(compute=_get_appointment_end, string='Appointment End Date', readonly=True, states={'Scheduled': [('readonly', False)]})
    state = fields.Selection(APPOINTMENT_STATUS, string='State', readonly=True, default=lambda *a: 'Scheduled')

    @api.multi
    def set_to_cancel(self):
        self.state = 'Cancel'

    @api.multi
    def set_to_visited(self):
        obj1 = self.env['oeh.medical.appointment.register.walkin']
        obj2 = self.env['unit.registration']
        reg_ids = []
        arv_ids = []
        for acc in self:
            if acc.patient:
                val_obj1 = {'patient': acc.patient.id, 
                   'dob': acc.patient.dob, 
                   'sex': acc.patient.sex, 
                   'marital_status': acc.patient.marital_status, 
                   'blood_type': acc.patient.blood_type, 
                   'rh': acc.patient.rh, 
                   'insurance': acc.patient.current_insurance.id, 
                   'date': datetime.datetime.now()}
                arv_ids = obj1.create(val_obj1)
                if arv_ids:
                    clinic_ids = False
                    unit_ids = False
                    emergency_ids = False
                    support_ids = False
                    if acc.patient_status == 'Out-Patient':
                        clinic_ids = arv_ids.id
                    elif acc.patient_status == 'In-Patient':
                        unit_ids = arv_ids.id
                    elif acc.patient_status == 'Emergency':
                        emergency_ids = arv_ids.id
                    elif acc.patient_status == 'Medical Support':
                        support_ids = arv_ids.id
                    val_obj2 = {'appointment_id': acc.id, 
                       'clinic_walkin_id': clinic_ids, 
                       'unit_walkin_id': unit_ids, 
                       'emergency_walkin_id': emergency_ids, 
                       'support_walkin_id': support_ids, 
                       'patient': acc.patient.id, 
                       'type': acc.patient_status, 
                       'unit': acc.unit.id, 
                       'doctor': acc.doctor.id, 
                       'schedule': 'Yes', 
                       'date': datetime.datetime.now()}
                    reg_ids = obj2.create(val_obj2)
                    if reg_ids:
                        self.state = 'Visited'
            else:
                raise UserError(_('Configuration error! \n Could not find any patient to create the registration !'))

        return {'name': 'Transactions', 'view_type': 'form', 
           'view_mode': 'form', 
           'res_id': reg_ids.id, 
           'res_model': 'unit.registration', 
           'type': 'ir.actions.act_window'}

    @api.model
    def create(self, vals):
        if vals.get('doctor') and vals.get('appointment_date'):
            self.check_physician_schedule(vals.get('doctor'), vals.get('appointment_date'))
        health_appointment = super(oeh_medical_appointment, self).create(vals)
        return health_appointment

    @api.multi
    def write(self, vals):
        doctor = False
        appointment_date = False
        if 'doctor' in vals:
            doctor = vals['doctor']
        if 'appointment_date' in vals:
            appointment_date = vals['appointment_date']
        self.check_physician_schedule(doctor or self.doctor.id, appointment_date or self.appointment_date)
        self.check_physician_availability(doctor or self.doctor.id, appointment_date or self.appointment_date)
        health_appointment = super(oeh_medical_appointment, self).write(vals)
        return health_appointment

    @api.multi
    def check_physician_schedule(self, doctor, appointment_date):
        available = False
        DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
        patient_line_obj = self.env['oeh.medical.physician.walkin.schedule']
        selected_day = datetime.datetime.strptime(appointment_date, DATETIME_FORMAT).strftime(DATETIME_FORMAT)
        if selected_day:
            avail_days = patient_line_obj.search([('name', '<=', selected_day), ('end_date', '>=', selected_day), ('physician_id', '=', doctor)], limit=1)
            if not avail_days:
                available = True
            else:
                raise UserError(_('Physician is not available. \n Please select ' + avail_days.replacement_doctor.name + ' !' + ' \n Notes: ' + avail_days.note))
        return available

    @api.multi
    def check_physician_availability(self, doctor, appointment_date):
        available = False
        day_info = ''
        DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
        patient_line_obj = self.env['oeh.medical.physician.line']
        selected_day = datetime.datetime.strptime(appointment_date, DATETIME_FORMAT).strftime('%A')
        if selected_day:
            avail_days = patient_line_obj.search([('name', '=', str(selected_day)), ('physician_id', '=', doctor)], limit=1)
            all_days = patient_line_obj.search([('physician_id', '=', doctor)])
            for avail in all_days:
                start_time = self.get_time_string(avail.start_time)
                end_time = self.get_time_string(avail.end_time)
                day_info = day_info + '- ' + avail.name + ' = ' + start_time + ' - ' + end_time + '\n '
                doctor_info = avail.physician_id.name

            if not avail_days:
                if all_days:
                    raise UserError(_(doctor_info + ' is not available on ' + str(selected_day) + '! \n\n [ Weekly Availability ] : \n ' + day_info))
            else:
                phy_start_time = self.get_time_string(avail_days.start_time).split(':')
                phy_end_time = self.get_time_string(avail_days.end_time).split(':')
                user_pool = self.env['res.users']
                user = user_pool.browse(self.env.uid)
                tz = pytz.timezone(user.partner_id.tz) or pytz.utc
                appointment_date = pytz.utc.localize(datetime.datetime.strptime(appointment_date, DATETIME_FORMAT)).astimezone(tz)
                t1 = datetime.time(int(phy_start_time[0]), int(phy_start_time[1]), 0)
                t3 = datetime.time(int(phy_end_time[0]), int(phy_end_time[1]), 0)
                t2 = datetime.time(appointment_date.hour, appointment_date.minute, 0)
                if not (t2 > t1 and t2 < t3):
                    raise UserError(_('Physician is not available on ' + str(t2) + '! \n ' + str(avail_days.name) + ' = ' + str(t1) + ' - ' + str(t3)))
                else:
                    available = True
        return available


class unit_registration_appointment(models.Model):
    _inherit = 'unit.registration'
    appointment_id = fields.Many2one(comodel_name='oeh.medical.appointment', string='Appointment No.')