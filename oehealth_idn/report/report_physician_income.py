# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from datetime import timedelta
from functools import partial

import psycopg2
import pytz

from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo.http import request
import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

class ReportPhysicanIncomeDetails(models.AbstractModel):

    _name = 'report.oehealth_idn.report_physiciandetails'

    @api.model
    def get_details(self, date_start=False, date_stop=False, physician_ids=False):
        """ Serialise the orders of the day information
        params: date_start, date_stop string representing the datetime of order
        """
        if not physician_ids:
            physician_ids = self.env['oeh.medical.physician'].search([])

        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        today = user_tz.localize(fields.Datetime.from_string(fields.Date.context_today(self)))
        today = today.astimezone(pytz.timezone('UTC'))
        if date_start:
            date_start = fields.Datetime.from_string(date_start)
        else:
            # start by default today 00:00:00
            date_start = today

        if date_stop:
            # set time to 23:59:59
            date_stop = fields.Datetime.from_string(date_stop)
        else:
            # stop by default today 23:59:59
            date_stop = today + timedelta(days=1, seconds=-1)

        # avoid a date_stop smaller than date_start
        date_stop = max(date_stop, date_start)

        date_start = fields.Datetime.to_string(date_start)
        date_stop = fields.Datetime.to_string(date_stop)

        incomes = []
        for physician_id in physician_ids:
            _logger.info(physician_id.name)
            sale_order_ids = self.env['sale.order'].search([
                ('date_order', '>=', date_start),
                ('date_order', '<=', date_stop),
                ('invoice_status', 'in', ['to invoice','invoiced']),
                ('doctor_id', '=', physician_id.id)])
            
            income_lines = []
            for sale_order_id in sale_order_ids:    
                for order_line in sale_order_id.order_line:
                    if order_line.product_id.item_type == 'Doctor':
                        _logger.info(order_line.product_id.name)
                        income_lines.append({
                            'date_order': sale_order_id.date_order,
                            'sale_order': sale_order_id.name,
                            'patient_name': sale_order_id.patient_id.name,
                            'arrival_id': sale_order_id.arrival_id.name,
                            'reg_id': sale_order_id.reg_id.name,
                            'product_name': order_line.product_id.name,
                            'qty': order_line.product_uom_qty,
                            'amount': order_line.price_subtotal
                        })
            
            if len(income_lines) > 0:
                income_vals = {
                    'physician_name': sale_order_id.doctor_id.name,
                    'income_lines': income_lines 
                }
                incomes.append(income_vals)
                
        _logger.info(incomes)
        return incomes

    @api.multi
    def render_html(self, docids, data=None):
        _logger.info("Render Report")
        data = dict(data or {})
        physicians = self.env['oeh.medical.physician'].browse(data['physician_ids'])
        incomes= self.get_details(data['date_start'], data['date_stop'], physicians)
        data.update({'incomes': incomes})
        return self.env['report'].render('oehealth_idn.report_physiciandetails', data)