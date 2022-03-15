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

        reg_id = self.env['unit.registration'].sudo().search([('id','=', walkin_id)])

        records.update({'docs': reg_id})

        for reg in reg_id:
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