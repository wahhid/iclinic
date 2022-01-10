# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00)
# [GCC 8.4.0]
# Embedded file name: D:\Workspaces\Odoo10\mod\Health\addons-custom\oehealth_idn\models\unit_registration_action.py
# Compiled at: 2018-12-27 04:13:42
from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
import datetime


class unit_registration_action(models.Model):
    _inherit = 'unit.registration'

    def _get_physician(self):
        """Return default physician value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain, limit=1)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    @api.multi
    def create_poly(self, model, val_obj, field_labels):
        obj = self.env[model]
        inv_ids = []
        for acc in self:
            if acc.patient:
                inv_ids = obj.create(val_obj)
                acc.write({field_labels: inv_ids.id})
            else:
                raise UserError(
                    _('Configuration error! \n Could not find any patient !'))

        return {'name': 'Action', 'view_type': 'form',
                'view_mode': 'form',
                'res_id': inv_ids.id,
                'res_model': model,
                'type': 'ir.actions.act_window'}

    @api.multi
    def view_poly(self, model, val_id, context, view_id=False):
        if view_id:
            domain = view_id
        else:
            domain = 'reg_id'
        return {'domain': "[('" + domain + "','=', " + str(val_id) + ')]',
                'name': 'Action',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': model,
                'type': 'ir.actions.act_window',
                'context': context}

    @api.multi
    def view_picking(self, context):
        return {'domain': [('partner_id', '=', self.patient.partner_id.id), '|', ('location_id.unit_ids.is_pharmacy', '=', True), ('location_dest_id.unit_ids.is_pharmacy', '=', True)],
                'name': 'Action',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'stock.picking',
                'type': 'ir.actions.act_window',
                'context': context
            }

    evaluation_id = fields.Many2one(
        comodel_name='oeh.medical.evaluation', string='Evaluation', copy=False, readonly=True)

    @api.multi
    def action_evaluation(self):
        model = 'oeh.medical.evaluation'
        field_id = self.evaluation_id
        field_labels = 'evaluation_id'

        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain, limit=1)
        doctor = False
        if user_ids:
            doctor = user_ids.id or False

<<<<<<< HEAD

        val_obj = {
            'reg_id': self.id, 
            'walkin': self.clinic_walkin_id.id or self.unit_walkin_id.id or self.emergency_walkin_id.id or self.support_walkin_id.id, 
            'patient': self.patient.id, 
=======
        val_obj = {
            'reg_id': self.id,
            'walkin': self.clinic_walkin_id.id or self.unit_walkin_id.id or self.emergency_walkin_id.id or self.support_walkin_id.id,
            'patient': self.patient.id,
>>>>>>> 8131d81b231df22e8d32fbdbe43187ef5f68ab98
            'doctor': doctor,
            'evaluation_start_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        if not field_id:
            return self.create_poly(model, val_obj, field_labels)
        else:
<<<<<<< HEAD
            
            context = {
                'default_reg_id': self.id, 
                'default_walkin': self.clinic_walkin_id.id or self.unit_walkin_id.id or self.emergency_walkin_id.id or self.support_walkin_id.id, 
                'default_patient': self.patient.id, 
=======

            context = {
                'default_reg_id': self.id,
                'default_walkin': self.clinic_walkin_id.id or self.unit_walkin_id.id or self.emergency_walkin_id.id or self.support_walkin_id.id,
                'default_patient': self.patient.id,
>>>>>>> 8131d81b231df22e8d32fbdbe43187ef5f68ab98
                'default_doctor': doctor,
                'default_evaluation_start_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            return self.view_poly(model, self.id, context)

    lab_id = fields.Many2one(comodel_name='oeh.medical.lab.test',
                             string='Lab Tests', copy=False, readonly=True)

    @api.multi
    def action_lab(self):
        model = 'oeh.medical.lab.test'
        field_id = self.lab_id
        field_labels = 'lab_id'
        context = {
            'default_reg_id': self.id,
            'default_walkin': self.clinic_walkin_id.id or self.unit_walkin_id.id or self.emergency_walkin_id.id or self.support_walkin_id.id or self.lab_test_walkin_id.id,
            'default_patient': self.patient.id,
            'default_requestor': self.doctor.id,
            'default_payment': self.payment,
            'default_company': self.company.id,
            'default_insurance': self.insurance.id,
            'default_employee_id': self.employee_id.id,
            'default_employee_id': self.payment_guarantor_discount_id.id
        }
        return self.view_poly(model, self.id, context)

    imaging_id = fields.Many2one(
        comodel_name='oeh.medical.imaging', string='Imaging Tests', copy=False, readonly=True)

    @api.multi
    def action_imaging(self):
        model = 'oeh.medical.imaging'
        field_id = self.imaging_id
        field_labels = 'imaging_id'
        val_obj = {'reg_id': self.id,
                   'walkin': self.clinic_walkin_id.id or self.unit_walkin_id.id or self.emergency_walkin_id.id or self.support_walkin_id.id,
                   'patient': self.patient.id,
                   'requestor': self.doctor.id,
                   'doctor_analyzing': self.doctor.id,
                   'test_type': 1}
        if not field_id:
            return self.create_poly(model, val_obj, field_labels)
        else:
            context = {'default_reg_id': self.id,
                       'default_walkin': self.clinic_walkin_id.id or self.unit_walkin_id.id or self.emergency_walkin_id.id or self.support_walkin_id.id,
                       'default_patient': self.patient.id,
                       'default_requestor': self.doctor.id,
                       'default_doctor_analyzing': self.doctor.id}
            return self.view_poly(model, self.id, context)

    prescription_id = fields.Many2one(
        comodel_name='oeh.medical.prescription', string='Prescriptions', copy=False, readonly=True)

    @api.multi
    def action_prescription(self):
        model = 'oeh.medical.prescription'
        field_id = self.prescription_id
        field_labels = 'prescription_id'
        val_obj = {'reg_id': self.id,
                   'walkin': self.clinic_walkin_id.id or self.unit_walkin_id.id or self.emergency_walkin_id.id or self.support_walkin_id.id,
                   'patient': self.patient.id,
                   'doctor': self.doctor.id,
                   'payment': self.payment,
                   'company': self.company.id,
                   'insurance': self.insurance.id,
                   'employee_id': self.employee_id.id}
        if not field_id:
            return self.create_poly(model, val_obj, field_labels)
        else:
            context = {
                'default_reg_id': self.id,
                'default_walkin': self.clinic_walkin_id.id or self.unit_walkin_id.id or self.emergency_walkin_id.id or self.support_walkin_id.id,
                'default_patient': self.patient.id,
                'default_doctor': self.doctor.id,
                'default_payment': self.payment,
                'default_company': self.company.id,
                'default_insurance': self.insurance.id,
                'default_employee_id': self.employee_id.id
            }
            return self.view_poly(model, self.id, context)

    gynecology_id = fields.Many2one(
        comodel_name='oeh.medical.gyneco', string='Gynecology', copy=False, readonly=True)

    @api.multi
    def action_gynecology(self):
        model = 'oeh.medical.gyneco'
        field_id = self.gynecology_id
        field_labels = 'gynecology_id'
        val_obj = {'reg_id': self.id,
                   'patient': self.patient.id}
        if not field_id:
            return self.create_poly(model, val_obj, field_labels)
        else:
            context = {'default_reg_id': self.id,
                       'default_patient': self.patient.id}
            return self.view_poly(model, self.id, context)

    newborn_id = fields.Many2one(
        comodel_name='oeh.medical.pediatrics.newborn', string='Newborns', copy=False, readonly=True)

    @api.multi
    def action_newborn(self):
        model = 'oeh.medical.pediatrics.newborn'
        field_id = self.newborn_id
        field_labels = 'newborn_id'
        if self.patient.sex != 'Female':
            raise UserError('The sex of the non-female patient')
        else:
            context = {'default_reg_id': self.id,
                       'default_mother': self.patient.id,
                       'default_doctor': self.doctor.id,
                       'default_institution': self.bed.institution.id}
            return self.view_poly(model, self.id, context)

    symptom_id = fields.Many2one(comodel_name='oeh.medical.pediatrics.psc',
                                 string='Pediatric Symptom', copy=False, readonly=True)

    @api.multi
    def action_symptom(self):
        model = 'oeh.medical.pediatrics.psc'
        field_id = self.symptom_id
        field_labels = 'symptom_id'
        val_obj = {'reg_id': self.id,
                   'patient': self.patient.id,
                   'doctor': self.doctor.id,
                   'evaluation_start': datetime.datetime.now()}
        if not field_id:
            return self.create_poly(model, val_obj, field_labels)
        else:
            context = {'default_reg_id': self.id,
                       'default_patient': self.patient.id,
                       'default_doctor': self.doctor.id}
            return self.view_poly(model, self.id, context)

    cardiac_id = fields.Many2one(
        comodel_name='oeh.medical.surgery.rcri', string='Cardiac', copy=False, readonly=True)

    @api.multi
    def action_cardiac(self):
        model = 'oeh.medical.surgery.rcri'
        field_id = self.cardiac_id
        field_labels = 'cardiac_id'
        val_obj = {'reg_id': self.id,
                   'patient': self.patient.id,
                   'doctor': self.doctor.id}
        if not field_id:
            return self.create_poly(model, val_obj, field_labels)
        else:
            context = {'default_reg_id': self.id,
                       'default_patient': self.patient.id,
                       'default_doctor': self.doctor.id}
            return self.view_poly(model, self.id, context)

    surgery_id = fields.Many2one(
        comodel_name='oeh.medical.surgery', string='Surgery', copy=False, readonly=True)

    @api.multi
    def action_surgery(self):
        model = 'oeh.medical.surgery'
        field_id = self.surgery_id
        field_labels = 'surgery_id'
        context = {'default_reg_id': self.id,
                   'default_patient': self.patient.id,
                   'default_surgeon': self.doctor.id,
                   'default_anesthetist': self.doctor.id,
                   'default_institution': self.bed.institution.id,
                   'default_building': self.bed.building.id}
        return self.view_poly(model, self.id, context)

    ophthalmology_id = fields.Many2one(
        comodel_name='oeh.medical.ophthalmology', string='Ophthalmology', copy=False, readonly=True)

    @api.multi
    def action_ophthalmology(self):
        model = 'oeh.medical.ophthalmology'
        field_id = self.ophthalmology_id
        field_labels = 'ophthalmology_id'
        val_obj = {'reg_id': self.id,
                   'patient': self.patient.id,
                   'doctor': self.doctor.id}
        if not field_id:
            return self.create_poly(model, val_obj, field_labels)
        else:
            context = {'default_reg_id': self.id,
                       'default_patient': self.patient.id,
                       'default_doctor': self.doctor.id}
            return self.view_poly(model, self.id, context)

    rounding_id = fields.Many2one(
        comodel_name='oeh.medical.patient.rounding', string='Rounding', copy=False, readonly=True)

    @api.multi
    def action_rounding(self):
        model = 'oeh.medical.patient.rounding'
        field_id = self.rounding_id
        field_labels = 'rounding_id'
        val_obj = {'inpatient_id': self.id,
                   'patient': self.patient.id,
                   'doctor': self.doctor.id}
        if not field_id:
            return self.create_poly(model, val_obj, field_labels)
        else:
            context = {'default_inpatient_id': self.id,
                       'default_patient': self.patient.id,
                       'default_doctor': self.doctor.id}
            return self.view_poly(model, self.id, context, 'inpatient_id')

    ambulatory_id = fields.Many2one(
        comodel_name='oeh.medical.patient.ambulatory', string='Ambulatory', copy=False, readonly=True)

    @api.multi
    def action_ambulatory(self):
        model = 'oeh.medical.patient.ambulatory'
        field_id = self.ambulatory_id
        field_labels = 'ambulatory_id'
        context = {'default_reg_id': self.id,
                   'default_patient': self.patient.id,
                   'default_doctor': self.doctor.id,
                   'default_evaluation_id': self.evaluation_id.id,
                   'default_evaluation_id': self.evaluation_id.indication.id}
        return self.view_poly(model, self.id, context)


class oeh_medical_evaluation(models.Model):
    _inherit = 'oeh.medical.evaluation'
    reg_id = fields.Many2one(
        comodel_name='unit.registration', string='Reg ID #', copy=False, readonly=True)


class oeh_medical_lab_test(models.Model):
    _inherit = 'oeh.medical.lab.test'
    reg_id = fields.Many2one(
        comodel_name='unit.registration', string='Reg ID #', copy=False, readonly=True)
    requestor = fields.Many2one(
        comodel_name='oeh.medical.physician', string='Doctor who requested the test')


class oeh_medical_imaging(models.Model):
    _inherit = 'oeh.medical.imaging'
    reg_id = fields.Many2one(
        comodel_name='unit.registration', string='Reg ID #', copy=False, readonly=True)
    doctor_analyzing = fields.Many2one(
        comodel_name='oeh.medical.physician', string='Doctor Analyzing')

    @api.onchange('test_type')
    def onchange_test_type(self):
        self.analysis = self.test_type.analysis


class oeh_medical_imaging_test_type(models.Model):
    _inherit = 'oeh.medical.imaging.test.type'
    analysis = fields.Text(string='Analysis')


class oeh_medical_prescription(models.Model):
    _inherit = 'oeh.medical.prescription'
    reg_id = fields.Many2one(
        comodel_name='unit.registration', string='Reg ID #', copy=False, readonly=True)
    unit_id = fields.Many2one(
        comodel_name='unit.administration', related='reg_id.unit', string='Unit')


class oeh_medical_gyneco(models.Model):
    _inherit = 'oeh.medical.gyneco'
    reg_id = fields.Many2one(
        comodel_name='unit.registration', string='Reg ID #', copy=False, readonly=True)


class oeh_medical_pediatrics_newborn(models.Model):
    _inherit = 'oeh.medical.pediatrics.newborn'
    reg_id = fields.Many2one(
        comodel_name='unit.registration', string='Reg ID #', copy=False, readonly=True)

    @api.multi
    def create_patient(self):
        obj = self.env['oeh.medical.patient']
        inv_ids = []
        for acc in self:
            if acc.mother:
                val_obj = {'newborn_id': acc.id, 'name': acc.name,
                           'dob': acc.birth_date,
                           'sex': acc.sex,
                           'marital_status': 'Single',
                           'street': acc.mother.street,
                           'is_baby': True,
                           'is_medical_record': True}
                inv_ids = obj.create(val_obj)
                if inv_ids:
                    inv_id = inv_ids.id
                acc.state = 'Patient'
            else:
                raise UserError(
                    _('Configuration error! \n Could not find any patient to create the patient !'))

        return {'name': 'Transactions', 'view_type': 'form',
                'view_mode': 'form',
                'res_id': inv_id,
                'res_model': 'oeh.medical.patient',
                'type': 'ir.actions.act_window'}


class oeh_medical_pediatrics_psc(models.Model):
    _inherit = 'oeh.medical.pediatrics.psc'
    reg_id = fields.Many2one(
        comodel_name='unit.registration', string='Reg ID #', copy=False, readonly=True)


class oeh_medical_surgery_rcri(models.Model):
    _inherit = 'oeh.medical.surgery.rcri'
    reg_id = fields.Many2one(
        comodel_name='unit.registration', string='Reg ID #', copy=False, readonly=True)


class oeh_medical_surgery(models.Model):
    _inherit = 'oeh.medical.surgery'
    reg_id = fields.Many2one(
        comodel_name='unit.registration', string='Reg ID #', copy=False, readonly=True)


class oeh_medical_ophthalmology(models.Model):
    _inherit = 'oeh.medical.ophthalmology'
    reg_id = fields.Many2one(
        comodel_name='unit.registration', string='Reg ID #', copy=False, readonly=True)


class oeh_medical_patient_rounding(models.Model):
    _inherit = 'oeh.medical.patient.rounding'
    inpatient_id = fields.Many2one(comodel_name='unit.registration', string='Registration Code',
                                   required=True, readonly=True, states={'Draft': [('readonly', False)]})


class oeh_medical_patient_ambulatory(models.Model):
    _inherit = 'oeh.medical.patient.ambulatory'
    reg_id = fields.Many2one(
        comodel_name='unit.registration', string='Reg ID #', copy=False, readonly=True)
