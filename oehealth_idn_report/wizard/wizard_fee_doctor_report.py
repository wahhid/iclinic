from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date
from dateutil.relativedelta import *
import xlwt
from xlwt import easyxf
import logging

_logger = logging.getLogger(__name__)


class WizardReportFeeDoctor(models.TransientModel):
    _name = 'wizard.report.fee.doctor'
    _description = 'Report Fee Doctor'

    @api.model
    def get_fee_doctor(self):

        # _logger.info(self.start_date)

        tglawal = datetime.strptime(self.start_date, "%Y-%m-%d").date()
        str_start_date = str(tglawal.year) + "-" + str(tglawal.month).zfill(2) + "-" + str(tglawal.day).zfill(
            2) + " 00:00:00"

        _logger.info(str_start_date)
        tglawal = datetime.strptime(str_start_date, "%Y-%m-%d %H:%M:%S") - relativedelta(hours=7)
        tglawal = tglawal.strftime("%Y-%m-%d %H:%M:%S")

        #=================================

        tglakhir = datetime.strptime(self.end_date, "%Y-%m-%d").date()
        _logger.info(tglakhir)
        str_end_date = str(tglakhir.year) + "-" + str(tglakhir.month).zfill(2) + "-" + str(tglakhir.day).zfill(
            2) + " 23:59:59"


        # _logger.info(tglakhir)

        args = []
        args.append((('tanggal', '>=', tglawal)))
        args.append((('tanggal', '<=', str_end_date)))
        # args.append((('Doctor', '=', self.billing_status)))

        # if self.billing_status == 'billing':
        #     args.append((('cara_bayar', '=', self.billing_status)))
        # elif self.billing_status == 'non_billing':
        #     args.append((('cara_bayar', '=', self.billing_status)))

        # if self.transaction_status == 'done':
        #     args.append((('state', '=', self.transaction_status)))
        # elif self.transaction_status == 'payment':
        #     args.append((('state', '=', self.transaction_status)))
        # elif self.transaction_status == 'cancel':
        #     args.append((('state', '=', self.transaction_status)))

        # if self.jenis_member == '1st':
        #     args.append((('jenis_member', '=', self.jenis_member)))
        # elif self.jenis_member == '2nd':
        #     args.append((('jenis_member', '!=', '1st')))


        order_lines = self.env['sale.order.line'].sudo().search(args)

        orderlines_datas = []

        for orderlin in order_lines:

            if orderlin.doctor.item_type == 'Doctor':

                vals = {}
                vals.update({'notrans': stiker.notrans})
                vals.update({'unit_kerja': stiker.unit_kerja.kode})
                vals.update({'name': stiker.name})
                

            orderlines_datas.append(vals)

        return {
            "transstikers": transstiker_datas
        }

    start_date = fields.Date(required=True, )
    end_date = fields.Date(required=True, )
  

    @api.multi
    def generate_report(self):
        data = {
            'date_start': self.start_date,
            'date_stop': self.end_date,
            'billing': self.billing_status,
            'transaction': self.transaction_status,
        }
        return self.env['report'].get_action([], 'oehealth_idn_report.report_requestdetails', data=data)
