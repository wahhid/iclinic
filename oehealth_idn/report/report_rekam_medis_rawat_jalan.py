# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from ast import walk
import logging
from datetime import datetime, timedelta, date
from functools import partial
from xml.dom.expatbuilder import parseString

import psycopg2
import pytz

from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo.http import request
import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

class ReportRekamMedisRawatJalan(models.AbstractModel):

    _name = 'report.oehealth_idn.report_rekammedisrawatjalan'

    @api.model
    def get_details(self, walkin_id=False, type=False):
        records = {}
        walkin = self.env['oeh.medical.appointment.register.walkin'].browse(walkin_id)
        #walkin = self.env['unit.registration'].search([('id','=',walkin_id)])
        #walkin = self.env['unit.registration'].search([('id','=',walkin_id)])

        walkinid = walkin.clinic_walkin_id.id or walkin.unit_walkin_id.id or walkin.emergency_walkin_id.id or walkin.support_walkin_id.id
        walkinids = self.env['oeh.medical.appointment.register.walkin'].search([('id','=',walkinid)])

        patient = {
            'patient_name':  walkin.patient.name,
            'medical_record': walkin.patient.medical_record,
            'sex': walkin.patient.sex,
            'age': walkin.patient.age,
            'ttl': walkin.patient.place_birth,
            'dob': walkin.patient.dob,
            'guarantor': walkin.payment,
            'employee_number': walkin.employee_id.employee_number,
            'insurance_name': walkin.insurance.ins_type.name,
            'insurance_no': walkin.insurance.ins_no
        }

        if len(walkin.clinic_ids) > 0:
            type = 'Out-Patient'
        
        if len(walkin.unit_ids) > 0:
            type = 'In-Patient'

        records.update({'type': type})
        records.update({'patient': patient})
        evaluations = []
        if type == 'Out-Patient':
            if len(walkin.clinic_ids) > 0:
                count = len(walkin.clinic_ids)
                _logger.info('Clinics IDS have ' + str(count) + ' records')
                for clinic_id in walkin.clinic_ids:
                    _logger.info(clinic_id.id)
                    evaluation_ids = self.env['oeh.medical.evaluation'].search([('reg_id','=', clinic_id.id)])
                    _logger.info(evaluation_ids)
                    for evaluation_id in evaluation_ids:
                        if evaluation_id.doctor.is_nurse:
                            vals = {
                                'evaluation_start_date': evaluation_id.evaluation_start_date,
                                'subjective': evaluation_id.subjective,
                                'weight': evaluation_id.weight,
                                'height': evaluation_id.height,
                                'imt': evaluation_id.imt,
                                'notes': evaluation_id.notes,
                                'notes_complaint': evaluation_id.notes_complaint,
                                'is_nurse': True,
                                'nurse': evaluation_id.doctor.name,
                                'is_doctor': False,
                                'doctor': False,
                            }
                            records.update({'nurse': vals})
                            #evaluations.append(vals)
                        if evaluation_id.doctor.is_doctor:
                            vals = {
                                'evaluation_start_date': evaluation_id.evaluation_start_date,
                                'subjective': evaluation_id.subjective,
                                'weight': evaluation_id.weight,
                                'height': evaluation_id.height,
                                'imt': evaluation_id.imt,
                                'notes': evaluation_id.notes,
                                'notes_complaint': evaluation_id.notes_complaint,
                                'is_nurse': False,
                                'nurse': False,
                                'is_doctor': True,
                                'doctor': evaluation_id.doctor.name,
                            }
                            records.update({'doctor': vals})
                            #evaluations.append(vals)
                #records.update({'evaluations': evaluations})

            if len(walkin.lab_test_ids) > 0:
                labs = []
                for lab_test in walkin.lab_test_ids:
                    labs.append(lab_test.name)
                records.update({'labs': labs})
            
            if len(walkin.emergency_ids) > 0:
                emergencies = []
                records.update({'emergencies': emergencies})

            if len(walkin.support_ids) > 0:
                supports = []
                records.update({'supports': supports})


        if type == 'In-Patient':
            if len(walkin.clinic_ids) > 0:
                count = len(walkin.unit_ids)
                _logger.info('Clinics IDS have ' + str(count) + ' records')
                for clinic_id in walkin.clinic_ids:
                    _logger.info(clinic_id.id)
                    evaluation_ids = self.env['oeh.medical.evaluation'].search([('reg_id','=', clinic_id.id)])
                    _logger.info(evaluation_ids)
                    for evaluation_id in evaluation_ids:
                        if evaluation_id.doctor.is_nurse:
                            vals = {
                                'evaluation_start_date': evaluation_id.evaluation_start_date,
                                'subjective': evaluation_id.subjective,
                                'weight': evaluation_id.weight,
                                'height': evaluation_id.height,
                                'imt': evaluation_id.imt,
                                'notes': evaluation_id.notes,
                                'notes_complaint': evaluation_id.notes_complaint,
                                'is_nurse': True,
                                'nurse': evaluation_id.doctor.name,
                                'is_doctor': False,
                                'doctor': False,
                            }
                            evaluations.append(vals)
                        if evaluation_id.doctor.is_doctor:
                            vals = {
                                'evaluation_start_date': evaluation_id.evaluation_start_date,
                                'subjective': evaluation_id.subjective,
                                'weight': evaluation_id.weight,
                                'height': evaluation_id.height,
                                'imt': evaluation_id.imt,
                                'notes': evaluation_id.notes,
                                'notes_complaint': evaluation_id.notes_complaint,
                                'is_nurse': False,
                                'nurse': False,
                                'is_doctor': True,
                                'doctor': evaluation_id.doctor.name,
                            }
                            evaluations.append(vals)
                records.update({'evaluations': evaluations})
                _logger.info(evaluations)


        records.update({'type': type})
        records.update({'patient': patient})
        # records.update({'type': type})
        # records.update({'patient': patient})
    
        evaluation_ids = self.env['oeh.medical.evaluation'].search([('reg_id','=', walkin.id)])
        _logger.info(evaluation_ids)

        evaluation = []
        alergi = []

        for evaluation_id in evaluation_ids:
            vals = {
                'alergi' : evaluation_id.allergy_history,
                'alergi_obat' : evaluation_id.lain_alergi_obat_makanan,
            }
            alergi.append(vals)

            pathologys = []

            x = datetime.strptime(evaluation_id.evaluation_start_date, "%Y-%m-%d %H:%M:%S")
            date_ev = x.strftime("%d %b %Y")

            if evaluation_id.doctor.is_nurse:
                for diagnos in evaluation_id.diagnostic_ids:
                    vals = {
                        'pathology_name': diagnos.name,
                    }
                    pathologys.append(vals)
                vals = {
                    'evaluation_start_date': date_ev,
                    'subjective': evaluation_id.subjective,
                    'weight': evaluation_id.weight,
                    'height': evaluation_id.height,
                    'imt': evaluation_id.imt,
                    'notes': evaluation_id.notes,
                    'notes_complaint': evaluation_id.notes_complaint,
                    'is_nurse': True,
                    'nurse': evaluation_id.doctor.name,
                    'is_doctor': False,
                    'doctor': False,
                    'pathologys': False,
                }
                evaluation.append(vals)
                #evaluations.append(vals)
            if evaluation_id.doctor.is_doctor:
                for diagnos in evaluation_id.diagnostic_ids:
                    vals = {
                        'pathology_name': diagnos.name,
                    }
                    pathologys.append(vals)
                vals = {
                    'evaluation_start_date': date_ev,
                    'subjective': evaluation_id.subjective,
                    'weight': evaluation_id.weight,
                    'height': evaluation_id.height,
                    'imt': evaluation_id.imt,
                    'notes': evaluation_id.notes,
                    'notes_complaint': evaluation_id.notes_complaint,
                    'is_nurse': False,
                    'nurse': False,
                    'is_doctor': True,
                    'doctor': evaluation_id.doctor.name,
                    'pathologys': pathologys,
                    'tindakan': evaluation_id.notes_complaint
                }
                evaluation.append(vals)

        records.update({'alergi_ids': alergi})
        records.update({'evaluation': evaluation})

        labs = []
<<<<<<< HEAD
        for lab_test in walkin.lab_test_ids:
=======
        for lab_test in walkinids.lab_test_ids:
>>>>>>> 10.0-yogi
            labs.append(lab_test.name)
        records.update({'labs': labs})

        return records

    @api.multi
    def render_html(self, docids, data=None):
        _logger.info("Render Report")
        data = dict(data or {}) 
        medis= self.get_details(data['walkin_id'])
        _logger.info(medis)
        data.update(medis)
        return self.env['report'].render('oehealth_idn.report_rekammedisrawatjalan', data)