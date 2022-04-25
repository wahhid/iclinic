from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
import logging


_logger = logging.getLogger(__name__)

class ReportRujukanExternal(models.AbstractModel):
    _name = 'report.oehealth_idn.report_rujukan_pasien'

    @api.model
    def _get_report_values(self, walkin_id=False, type=False):
        records = {}
        
        reg_id = self.env['unit.registration'].sudo().search([('id','=', walkin_id)])

        age = ''
        if reg_id[0].patient.dob:
            dob = datetime.strptime(reg_id[0].patient.dob, "%Y-%m-%d")
            age_calc = (datetime.today() - dob).days/365
            age = str(age_calc) + ' Tahun'
            age = age
        
        records.update({'age': age})
        records.update({'docs': reg_id})

        
        evaluation_ids = self.env['oeh.medical.evaluation'].sudo().search([('reg_id','=', reg_id.id)], order='create_date desc')
        
        evaluation_list = []
        for ev in evaluation_ids:
            _logger.info(ev.doctor.is_doctor)
            # if ev.doctor.is_doctor == 'True':
            pathology_list = []
            for diag in ev.diagnostic_ids:
                pathology_list.append({
                    'pathology': diag.name
                })

            evaluation_list.append({
                'is_nurse' : ev.doctor.is_nurse,
                'is_doctor': ev.doctor.is_doctor,
                'notes_complaint': ev.notes_complaint,
                'systolic': ev.systolic,
                'diastolic': ev.diastolic,
                'temperature': ev.temperature,
                'nadi': ev.nadi,
                'respiratory_rate': ev.respiratory_rate,
                'osat': ev.osat,
                'gcs_e': ev.gcs_e,
                'gcs_v': ev.gcs_v,
                'gcs_m': ev.gcs_m,
                'total_gcs': ev.total_gcs,
                'gds': ev.gds,
                'pathology_list': pathology_list
            })

                
        records.update({'evaluation_list': evaluation_list})
        
        prescription_ids = self.env['oeh.medical.prescription'].sudo().search([('reg_id','=', reg_id.id)], order='create_date desc')
        
        prescription_list = []
        for pres in prescription_ids:
            for pres_line in pres.prescription_line:
                prescription_list.append({
                    'common_dosage': pres_line.common_dosage.name,
                    'name': pres_line.name.name,
                    'dose_route': pres_line.dose_route.name
                })
            _logger.info(pres.prescription_line)

        _logger.info("===PRESCRIPTION")        
        _logger.info(prescription_ids)
        _logger.info(prescription_list)

        records.update({'prescription_list': prescription_list}) 

        return records

    @api.multi
    def render_html(self, docids, data=None):
        _logger.info("Render Report")
        data = dict(data or {}) 
        medis= self._get_report_values(data['walkin_id'])
        _logger.info(medis)
        data.update(medis)
        return self.env['report'].render('oehealth_idn.report_rujukan_pasien', data)