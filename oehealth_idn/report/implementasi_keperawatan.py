from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from odoo.tools import formatLang
import logging


_logger = logging.getLogger(__name__)

class ReportImplementasiKeperawatan(models.AbstractModel):
    _name = 'report.oehealth_idn.report_implementasi_keperawatan'

    @api.model
    def _get_report_values(self, activeid):

        sale_order = self.env['sale.order'].sudo().search([('reg_id','=', activeid)])

        sale_order_list = []

        for app in sale_order:

            for line in app.sale_order_line:

                sale_order_list.append({
                    'tanggal': app.date_order,
                    'tujuan' : line.tujuan,
                    'doctor_name': app.doctor_id.name,
                })
 
        _logger.info("====== DATA DATA DATA =========")
        _logger.info(sale_order)
        _logger.info(sale_order_list)

        return sale_order_list
        


    @api.model
    def render_html(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        
        activeid = self.env.context.get('active_id')

        total = []
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))


        sale_order_list = self._get_report_values(activeid)

        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'sale_order_list': sale_order_list,
        }
        return self.env['report'].render('oehealth_idn.report_implementasi_keperawatan', docargs)