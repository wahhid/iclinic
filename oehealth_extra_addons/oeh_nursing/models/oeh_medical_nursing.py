# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
# [GCC 8.4.0]
# Embedded file name: D:\DEV\Workspaces\odoo10\addons_custom\oehealth_extra_addons\oeh_nursing\models\oeh_medical_nursing.py
# Compiled at: 2017-03-07 13:01:22
from odoo import fields, api, models, _
from odoo.exceptions import UserError
import datetime

class OeHealthPatientRoundingProcedures(models.Model):
    _name = 'oeh.medical.patient.rounding.procedure'
    _description = 'Patient Procedures For Roundings'
    name = fields.Many2one('oeh.medical.patient.rounding', string='Rouding')
    procedures = fields.Many2one('oeh.medical.procedure', string='Procedures', required=True)
    notes = fields.Text('Notes')


class OeHealthPatientRoundingMedicines(models.Model):
    _name = 'oeh.medical.patient.rounding.medicines'
    _description = 'Patient Medicines For Roundings'
    name = fields.Many2one('oeh.medical.patient.rounding', string='Rounding')
    medicine = fields.Many2one('oeh.medical.medicines', string='Medicines', domain=[('medicament_type', '=', 'Medicine')], required=True)
    qty = fields.Integer('Quantity', default=lambda *a: 1)
    notes = fields.Text('Comment')


class OeHealthPatientRoundingManagement(models.Model):
    _name = 'oeh.medical.patient.rounding'
    _description = 'Patient Rounding Management'
    STATUS = [
     ('Draft', 'Draft'),
     ('Completed', 'Completed')]
    EVOLUTION = [
     ('Status Quo', 'Status Quo'),
     ('Improving', 'Improving'),
     ('Worsening', 'Worsening')]

    @api.multi
    def _get_patient_rounding(self):
        """Return default physician value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    name = fields.Char(string='Rounding #', size=128, readonly=True, default=lambda *a: '/')
    inpatient_id = fields.Many2one('oeh.medical.inpatient', string='Registration Code', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help='Patient Name', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    doctor = fields.Many2one('oeh.medical.physician', string='Physician', help='Physician Name', domain=[('is_pharmacist', '=', False)], required=True, readonly=True, states={'Draft': [('readonly', False)]}, default=_get_patient_rounding)
    evaluation_start_date = fields.Datetime(string='Start date & time', required=True, readonly=True, states={'Draft': [('readonly', False)]}, default=lambda *a: datetime.datetime.now())
    evaluation_end_date = fields.Datetime(string='End date & time', readonly=True, states={'Draft': [('readonly', False)]})
    environmental_assessment = fields.Char('Environment', help='Environment assessment. State any disorder in the room.', size=128, readonly=True, states={'Draft': [('readonly', False)]})
    weight = fields.Integer(string='Weight', help='Measured weight, in kg', readonly=True, states={'Draft': [('readonly', False)]})
    pain = fields.Boolean(string='Pain', help='Check if the patient is in pain', readonly=True, states={'Draft': [('readonly', False)]})
    pain_level = fields.Boolean(string='Pain Level', help='Enter the pain level, from 1 to 10', readonly=True, states={'Draft': [('readonly', False)]})
    potty = fields.Boolean(string='Potty', help='Check if the patient needs to urinate / defecate', readonly=True, states={'Draft': [('readonly', False)]})
    position = fields.Boolean(string='Position', help='Check if the patient needs to be repositioned or is unconfortable', readonly=True, states={'Draft': [('readonly', False)]})
    proximity = fields.Boolean(string='Proximity', help='Check if personal items, water, alarm, ... are not in easy reach', readonly=True, states={'Draft': [('readonly', False)]})
    pump = fields.Boolean(string='Pumps', help='Check if personal items, water, alarm, ... are not in easy reach', readonly=True, states={'Draft': [('readonly', False)]})
    personal_needs = fields.Boolean(string='Personal needs', help='Check if the patient requests anything', readonly=True, states={'Draft': [('readonly', False)]})
    systolic = fields.Integer(string='Systolic Pressure', readonly=True, states={'Draft': [('readonly', False)]})
    diastolic = fields.Integer(string='Diastolic Pressure', readonly=True, states={'Draft': [('readonly', False)]})
    bpm = fields.Integer(string='Heart Rate', help='Heart rate expressed in beats per minute', readonly=True, states={'Draft': [('readonly', False)]})
    respiratory_rate = fields.Integer(string='Respiratory Rate', help='Respiratory rate expressed in breaths per minute', readonly=True, states={'Draft': [('readonly', False)]})
    osat = fields.Integer(string='Oxygen Saturation', help='Oxygen Saturation(arterial)', readonly=True, states={'Draft': [('readonly', False)]})
    temperature = fields.Float(string='Temperature', help='Temperature in celsius', readonly=True, states={'Draft': [('readonly', False)]})
    diuresis = fields.Integer(string='Diuresis', help='volume in ml', readonly=True, states={'Draft': [('readonly', False)]})
    urinary_catheter = fields.Integer(string='Urinary Catheter', readonly=True, states={'Draft': [('readonly', False)]})
    glycemia = fields.Integer(string='Glycemia', help='Blood Glucose level', readonly=True, states={'Draft': [('readonly', False)]})
    depression = fields.Boolean(string='Depression Signs', help='Check this if the patient shows signs of depression', readonly=True, states={'Draft': [('readonly', False)]})
    evolution = fields.Selection(EVOLUTION, string='Evolution', readonly=True, states={'Draft': [('readonly', False)]})
    round_summary = fields.Text(string='Round Summary', readonly=True, states={'Draft': [('readonly', False)]})
    warning = fields.Boolean(string='Warning', help='Check this box to alert the supervisor about this patient rounding. A warning icon will be shown in the rounding list', readonly=True, states={'Draft': [('readonly', False)]})
    procedures = fields.One2many('oeh.medical.patient.rounding.procedure', 'name', string='Procedures', help='List of the procedures in this rounding. Please enter the first one as the main procedure', readonly=True, states={'Draft': [('readonly', False)]})
    medicaments = fields.One2many('oeh.medical.patient.rounding.medicines', 'name', string='Medicines', help='List of the medicines assigned in this rounding', readonly=True, states={'Draft': [('readonly', False)]})
    state = fields.Selection(STATUS, string='State', readonly=True, default=lambda *a: 'Draft')

    @api.multi
    def unlink(self):
        for nursing in self.filtered(lambda nursing: nursing.state not in ('Draft', )):
            raise UserError(_('You can not delete rounding information which is not in "Draft" state !!'))

        return super(OeHealthPatientRoundingManagement, self).unlink()

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('oeh.medical.patient.rounding')
        vals['name'] = sequence
        return super(OeHealthPatientRoundingManagement, self).create(vals)

    @api.multi
    def set_to_completed(self):
        return self.write({'state': 'Completed', 'evaluation_end_date': datetime.datetime.now()})

    @api.multi
    def print_patient_evaluation(self):
        return self.env['report'].get_action(self, 'oehealth_extra_addons.report_patient_rounding_evaluation')


class OeHealthPatientAmbulatoryProcedures(models.Model):
    _name = 'oeh.medical.patient.ambulatory.procedure'
    _description = 'Patient Procedures For Ambulatory'
    name = fields.Many2one('oeh.medical.patient.ambulatory', string='Ambulatory')
    procedures = fields.Many2one('oeh.medical.procedure', string='Procedures', required=True)
    notes = fields.Text('Notes')


class OeHealthPatientAmbulatoryMedicines(models.Model):
    _name = 'oeh.medical.patient.ambulatory.medicines'
    _description = 'Patient Medicines For Ambulatory'
    name = fields.Many2one('oeh.medical.patient.ambulatory', string='Ambulatory')
    medicine = fields.Many2one('oeh.medical.medicines', string='Medicines', domain=[('medicament_type', '=', 'Medicine')], required=True)
    qty = fields.Integer(string='Quantity', default=lambda *a: 1)
    notes = fields.Text(string='Comment')


class OeHealthPatientAmbulatoryCare(models.Model):
    _name = 'oeh.medical.patient.ambulatory'
    _description = 'Patient Ambulatory Management'
    STATUS = [
     ('Draft', 'Draft'),
     ('Completed', 'Completed')]
    EVOLUTION = [
     ('Initial', 'Initial'),
     ('Status Quo', 'Status Quo'),
     ('Improving', 'Improving'),
     ('Worsening', 'Worsening')]

    @api.multi
    def _get_patient_ambulatory(self):
        """Return default physician value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    name = fields.Char(string='Session #', size=128, readonly=True, default=lambda *a: '/')
    evaluation_id = fields.Many2one('oeh.medical.evaluation', string='Evaluation #', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    base_condition = fields.Many2one('oeh.medical.pathology', string='Condition', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help='Patient Name', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    doctor = fields.Many2one('oeh.medical.physician', string='Physician', help='Physician Name', domain=[('is_pharmacist', '=', False)], required=True, readonly=True, states={'Draft': [('readonly', False)]}, default=_get_patient_ambulatory)
    ordering_doctor = fields.Many2one('oeh.medical.physician', string='Requested by', help='Physician Name', domain=[('is_pharmacist', '=', False)], readonly=True, states={'Draft': [('readonly', False)]})
    evaluation_start_date = fields.Datetime(string='Start date & time', required=True, readonly=True, states={'Draft': [('readonly', False)]}, default=lambda *a: datetime.datetime.now())
    evaluation_end_date = fields.Datetime(string='End date & time', readonly=True, states={'Draft': [('readonly', False)]})
    systolic = fields.Integer(string='Systolic Pressure', readonly=True, states={'Draft': [('readonly', False)]})
    diastolic = fields.Integer(string='Diastolic Pressure', readonly=True, states={'Draft': [('readonly', False)]})
    bpm = fields.Integer(string='Heart Rate', help='Heart rate expressed in beats per minute', readonly=True, states={'Draft': [('readonly', False)]})
    respiratory_rate = fields.Integer(string='Respiratory Rate', help='Respiratory rate expressed in breaths per minute', readonly=True, states={'Draft': [('readonly', False)]})
    osat = fields.Integer(string='Oxygen Saturation', help='Oxygen Saturation(arterial)', readonly=True, states={'Draft': [('readonly', False)]})
    temperature = fields.Float(string='Temperature', help='Temperature in celsius', readonly=True, states={'Draft': [('readonly', False)]})
    glycemia = fields.Integer(string='Glycemia', help='Blood Glucose level', readonly=True, states={'Draft': [('readonly', False)]})
    evolution = fields.Selection(EVOLUTION, string='Evolution', readonly=True, states={'Draft': [('readonly', False)]})
    session_notes = fields.Text(string='Notes', readonly=True, states={'Draft': [('readonly', False)]})
    procedures = fields.One2many('oeh.medical.patient.ambulatory.procedure', 'name', string='Procedures', help='List of the procedures in this ambulatory. Please enter the first one as the main procedure', readonly=True, states={'Draft': [('readonly', False)]})
    medicaments = fields.One2many('oeh.medical.patient.ambulatory.medicines', 'name', string='Medicines', help='List of the medicines assigned in this ambulatory', readonly=True, states={'Draft': [('readonly', False)]})
    state = fields.Selection(STATUS, string='State', readonly=True, default=lambda *a: 'Draft')

    @api.multi
    def unlink(self):
        for nursing in self.filtered(lambda nursing: nursing.state not in ('Draft', )):
            raise UserError(_('You can not delete information which is not in "Draft" state !!'))

        return super(OeHealthPatientAmbulatoryCare, self).unlink()

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('oeh.medical.patient.ambulatory')
        vals['name'] = sequence
        return super(OeHealthPatientAmbulatoryCare, self).create(vals)

    @api.multi
    def set_to_completed(self):
        return self.write({'state': 'Completed', 'evaluation_end_date': datetime.datetime.now()})