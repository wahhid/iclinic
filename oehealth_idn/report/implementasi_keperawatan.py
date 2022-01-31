from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
from odoo.tools import formatLang
import logging


_logger = logging.getLogger(__name__)

class ReportImplementasiKeperawatan(models.AbstractModel):
    _name = 'report.oehealth_idn.report_implementasi_keperawatan'

    @api.model
    def _get_report_values(self, walkin_id=False, type=False):
        records = {}
        sale_order_list = []

        unit_register_ids = self.env['unit.registration'].sudo().search([('clinic_walkin_id','=', walkin_id)])
        records.update({'no_rm': unit_register_ids[0].patient.medical_record}) 
        records.update({'patient_name': unit_register_ids[0].patient.name}) 
        records.update({'dob': unit_register_ids[0].patient.dob})
        records.update({'doctor': unit_register_ids[0].doctor.name})
        records.update({'bed': unit_register_ids[0].bed.name})

        for reg in unit_register_ids:
            sale_order_ids = self.env['sale.order'].sudo().search([('reg_id','=', reg.id)])
            
            for order in sale_order_ids:
                sale_order_line_ids = self.env['sale.order.line'].sudo().search([('order_id','=', order.id)])

                for line in sale_order_line_ids:
                    date_order = order.date_order

                    if line.product_id.type == 'service':
                        vals = {
                            'tanggal': date_order,
                            'tujuan' : line.name,
                            'doctor_name': order.doctor_id.name,
                        }
                        sale_order_list.append(vals)

        records.update({'sale_order_list': sale_order_list}) 

        _logger.info("==Records")
        _logger.info(sale_order_list)
        _logger.info(records)

        return records

    @api.multi
    def render_html(self, docids, data=None):
        _logger.info("Render Report")
        data = dict(data or {}) 
        medis= self._get_report_values(data['walkin_id'])
        _logger.info(medis)
        data.update(medis)
        return self.env['report'].render('oehealth_idn.report_implementasi_keperawatan', data)