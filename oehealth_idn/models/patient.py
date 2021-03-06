# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
# [GCC 8.4.0]
# Embedded file name: D:\Workspaces\Odoo10\mod\Health\addons-custom\oehealth_idn\models\patient.py
# Compiled at: 2019-01-16 14:05:16
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DSDF, DEFAULT_SERVER_DATETIME_FORMAT

class oeh_medical_patient(models.Model):
    _inherit = 'oeh.medical.patient'

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            tit = '[%s] %s' % (record.medical_record, record.name)
            res.append((record.id, tit))

        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=80):
        args = args or []
        if name:
            args = ['|', ('name', operator, name), ('medical_record', operator, name)] + args
        record = self.search(args, limit=limit)
        return record.name_get()

    @api.depends('identification_code')
    def _reformat_medical_record(self):
        for record in self:
            idnum_str = record.identification_code
            if len(idnum_str) == 9:
                record.medical_record = idnum_str[:3] + '-' + idnum_str[3:6] + '-' + idnum_str[6:9]
            else:
                record.medical_record = idnum_str

    @api.constrains('dob')
    def _check_birthday(self):
        """
        This method used to check birthday should be less then current date.
        """
        curr_date = datetime.strftime(datetime.today().date(), DSDF)
        for rec in self:
            if rec.dob and rec.dob > curr_date:
                raise ValidationError(_('Date of Birth should be                     less than the Current Date!'))

    @api.multi
    def _inpatient_count(self):
        oe_admission = self.env['unit.registration']
        for adm in self:
            domain = [
             (
              'patient', '=', adm.id)]
            admission_ids = oe_admission.search(domain)
            admissions = oe_admission.browse(admission_ids)
            admission_count = 0
            for ad in admissions:
                admission_count += 1

            adm.inpatient_count = admission_count

        return True

    identification_code = fields.Char(string='Medical Record', readonly=False, index=True)
    medical_record = fields.Char(compute=_reformat_medical_record, string='Medical Record', store=True, readonly=True, index=True)
    current_insurance = fields.Many2one('medical.insurance', string='Insurance', domain="[('patient','=', active_id),('state','=','Active')]", index=True, help='Insurance information. You may choose from the different insurances belonging to the patient')
    inpatient_count = fields.Integer(compute=_inpatient_count, string='Admission / Discharge')
    is_medical_record = fields.Boolean(string='Patient with Medical Record')

    @api.model
    def create(self, vals):
        vals['name'] = vals['name'].upper()
        if vals['street']:
            vals['street'] = vals['street'].upper()
        res = super(oeh_medical_patient, self).create(vals)
        if vals['is_medical_record']:
            sequence = self.env['ir.sequence'].next_by_code('oeh.medical.patient')
        else:
            sequence = self.env['ir.sequence'].next_by_code('oeh.medical.patient.dummy')
        res.update({'identification_code': sequence})
        return res

    @api.multi
    def create_registration(self):
        return {'name': 'Transactions', 
           'view_type': 'form', 
           'view_mode': 'form', 
           'res_model': 'oeh.medical.appointment.register.walkin', 
           'type': 'ir.actions.act_window', 
           'context': {'default_patient': self.id, 
                       'default_dob': self.dob, 
                       'default_marital_status': self.marital_status, 
                       'default_rh': self.rh, 
                       'default_sex': self.sex, 
                       'default_blood_type': self.blood_type, 
                       'default_insurance': self.current_insurance.id}}

    @api.multi
    def view_medical_record(self):
        form_view_id = self.env.ref('oehealth.oeh_medical_patient_view').id
        return {'res_id': self.id, 
           'name': 'Medical Record', 
           'view_type': 'form', 
           'view_mode': 'form', 
           'views': [
                   [
                    form_view_id, 'form']], 
           'res_model': 'oeh.medical.patient', 
           'type': 'ir.actions.act_window'}

    @api.multi
    def print_patient_stiker(self):
        return self.env['report'].get_action(self, 'oehealth_idn.report_stiker_pasien')


class oeh_medical_patient_family(models.Model):
    _inherit = 'oeh.medical.patient.family'
    mobile = fields.Char(string='Mobile')
    address = fields.Text(string='Address')