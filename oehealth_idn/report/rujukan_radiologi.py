from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
import logging


_logger = logging.getLogger(__name__)

class ReportRadiologi(models.AbstractModel):
    _name = 'report.oehealth_idn.report_rujukan_radiologi'

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

            evaluation_list.append({'is_doctor': ev.doctor.is_doctor,'notes_complaint': ev.notes_complaint})
            _logger.info(ev.notes_complaint)

        records.update({'evaluation_list': evaluation_list}) 

        _logger.info("==Records")
        _logger.info(evaluation_list)
        _logger.info(evaluation_ids)

        return records

    @api.multi
    def render_html(self, docids, data=None):
        _logger.info("Render Report")
        data = dict(data or {}) 
        medis= self._get_report_values(data['walkin_id'])
        _logger.info(medis)
        data.update(medis)
        return self.env['report'].render('oehealth_idn.report_rujukan_radiologi', data)