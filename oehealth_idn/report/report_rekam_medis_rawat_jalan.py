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
        walkin = self.env['unit.registration'].search([('id','=',walkin_id)])
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
        for lab_test in walkin.lab_id:
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