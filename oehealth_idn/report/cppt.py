from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
import logging


_logger = logging.getLogger(__name__)

class ReportCPPT(models.AbstractModel):
    _name = 'report.oehealth_idn.report_cppt'

    @api.model
    def _get_report_values(self, walkin_id=False, type=False):
        records = {}
        evaluation_list = []

        reg_id = self.env['unit.registration'].sudo().search([('id','=', walkin_id)])

        records.update({'docs': reg_id})

        for reg in reg_id:
            evaluation_ids = self.env['oeh.medical.evaluation'].sudo().search([('reg_id','=', reg.id)])
            
            for ev in evaluation_ids:

                    vals = {
                        'S': ev.subjective,
                        'O': {
                            'bb': ev.weight,
                            'tb': ev.height,
                            'imt': ev.bmi,
                        },
                        'A': ev.notes,
                        'P': ev.notes_complaint,
                        'ppa': ev.doctor.name,
                        'tanggal': ev.evaluation_start_date,
                        'dpjp': reg.doctor.name,
                    }
                    evaluation_list.append(vals)

        records.update({'evaluation_list': evaluation_list}) 

        _logger.info("==Records")
        _logger.info(evaluation_list)
        _logger.info(records)

        return records

    @api.multi
    def render_html(self, docids, data=None):
        _logger.info("Render Report")
        data = dict(data or {}) 
        medis= self._get_report_values(data['walkin_id'])
        _logger.info(medis)
        data.update(medis)
        return self.env['report'].render('oehealth_idn.report_cppt', data)