from odoo import fields, models, api, _
from odoo.exceptions import Warning, ValidationError, UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from datetime import datetime
import logging
import time

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class WizardAccountVoucherReport(models.TransientModel):
	_name = 'account.voucher.report'

	date_from = fields.Date("Date from", required=True, default=lambda *a: time.strftime('%Y-%m-%d'))
	date_to = fields.Date("Date to", required=True, default=lambda *a: time.strftime('%Y-%m-%d'))
	res_user_id = fields.Many2one('res.user')

	@api.multi
	def print_report(self):
		report_obj = self.env['report']
		template = 'jakc_account_voucher.report_accountvoucher_summary'
		report = report_obj._get_report_from_name(template)

		domain = {
			'date_start': self.date_start,
			'date_end': self.date_end,
		}

		vals = {
			'ids': self.ids,
			'model': report.model,
			'form': domain
		}

		"""get_action() otomatis akan memanggil render_html() di report"""
		return report_obj.get_action(self, template, data=vals)



class ReportAccountVoucherSummary(models.AbstractModel):

	_name = 'report.jakc_account_voucher.report_accountvoucher_summary'
	_template = 'jakc_account_voucher.report_accountvoucher_summary'

	@api.model
	def render_html(self, docids, data=None):
		if data is None:
			return

		date_start = data['form']['date_start']
		date_end = data['form']['date_end']

		report_obj = self.env['report']
		docs = self._get_rekap_data(date_start, date_end)

		LOCAL_FORMAT = '%d/%m/%Y'

		vals = {
			'docs': docs,
			'date_start': datetime.strptime(date_start, DATE_FORMAT).strftime(LOCAL_FORMAT),
			'date_end': datetime.strptime(date_end, DATE_FORMAT).strftime(LOCAL_FORMAT),
		}

		return report_obj.render(self._template, values=vals)


	def _get_rekap_data(self, date_start, date_end):

		date_start_obj = datetime.strptime(date_start, DATE_FORMAT).date()
		date_end_obj = datetime.strptime(date_end, DATE_FORMAT).date()
		date_count = (date_end_obj - date_start_obj).days + 1
		data = []
		domain = [
			('date', '>=', date_start),
			('date', '<=', date_end)
		]

		account_voucher_ids = self.env['account.voucher'].search(domain)
		for account_voucher_id in account_voucher_ids:
			data.append({
			'data': account_voucher_id.date,
			'name': account_voucher_id.name,
			'operating_unit_id':  account_voucher_id.operating_unit_id.name,
			'account': account_voucher_id.payment_journal_id.default_debit_account_id.name,
			'total': amount,
			'state': account_voucher_id.state
			})

		return data