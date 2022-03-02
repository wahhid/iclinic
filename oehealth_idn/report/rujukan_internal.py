from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
import logging


_logger = logging.getLogger(__name__)

class ReportRujukanInternal(models.AbstractModel):
    _name = 'report.oehealth_idn.report_rujukan_internal'

    @api.model
    def _get_report_values(self, walkin_id=False, type=False):
        records = {}
        
        reg_id = self.env['unit.registration'].sudo().search([('id','=', walkin_id)])
        
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

            rpp = False
            if ev.lain_rpp:
                rpp = True

            evaluation_list.append({
                'is_doctor': ev.doctor.is_doctor,
                'notes_complaint': ev.notes_complaint,
                'dm_stroke_p': ev.dm_stroke_p,
                'katarak': ev.katarak,
                'hipertensi_p': ev.hipertensi_p,
                'jantung_p': ev.jantung_p,
                'kolesterol': ev.kolesterol,
                'liver': ev.liver,
                'asam_urat': ev.asam_urat,
                'pendarahan': ev.pendarahan,
                'rpp': rpp,
                'lain_rpp': ev.lain_rpp,
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
        return self.env['report'].render('oehealth_idn.report_rujukan_internal', data)