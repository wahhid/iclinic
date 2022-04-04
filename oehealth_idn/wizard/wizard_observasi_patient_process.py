from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date
from dateutil.relativedelta import *
import xlwt
from xlwt import easyxf
import logging

_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    _logger.debug('Cannot `import xlwt`.')

try:
    from cStringIO import StringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')

try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')

_logger = logging.getLogger(__name__)


class WizardReportObservasi(models.TransientModel):
    _name = 'wizard.report.observasi'
    _description = 'Observasi Patient'


    reg_id = fields.Many2one(comodel_name="unit.registration", string="Reg.Id", required=False,)
    start_date = fields.Date(required=True, )
    end_date = fields.Date(required=True, )
    report_filename = fields.Char('Filename', size=100, readonly=True, default='ObservasiReport.xlsx')
    report_file = fields.Binary('File', readonly=True)
    report_printed = fields.Boolean('Report Printed', default=False, readonly=True)

    @api.multi
    def generate_report_excel(self):

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

        for wizard in self:
            sheet1 = "Observasi"
            sheet2 = "Notes"

            fp = StringIO()
            workbook = xlsxwriter.Workbook(fp)

            # format_main_header = workbook.add_format({'font_size': 14, 'bg_color': 'silver', 'bold': 1, 'border': 1,
            #                                         'align': 'center', 'valign': 'vcenter'})
            format_header = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center',
                                                'valign': 'vcenter', 'bg_color': 'silver'})
            header = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center',
                                        'valign': 'vcenter', 'bg_color': 'silver'})
            left_header = workbook.add_format({'bold': 1, 'border': 1, 'align': 'left',
                                            'valign': 'vcenter','bg_color': 'silver'})
            # format_cell = workbook.add_format({'border': 1, 'align': 'center'})
            # worksheet.merge_range(row, col, row + 1, col + 3, "Time Duration(Hours)", header)
        

            active_id = self.env['oeh.medical.evaluation'].search([('reg_id','=',self.env.context.get('active_id')), ('create_date', '>=', tglawal), ('create_date', '<=', str_end_date)])

            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': 1,'border': 1,})

            regis_id = self.env['unit.registration'].browse(self.env.context.get('active_id'))

            # Data Patient
            worksheet.write(1, 0, _('No.RM '), left_header)
            worksheet.write(1, 1, regis_id.patient.medical_record, bold)
            worksheet.write(2, 0, _('Nama Pasien '), left_header)
            worksheet.write(2, 1, regis_id.patient.name, bold)
            worksheet.write(1, 3, _('Tanggal Lahir '), left_header)
            worksheet.write(1, 4, regis_id.patient.dob, bold)
            worksheet.write(2, 3, _('NPP/No.BPJS'), left_header)
            if regis_id.patient.is_employee:
                worksheet.write(2, 4, regis_id.patient.employee_number, bold)
            worksheet.write(1, 6, _('Ruang Perawatan'), left_header)
            if regis_id.room_id.name:
                worksheet.write(1, 7, regis_id.room_id.name, bold)
            worksheet.write(2, 6, _('Tanggal Masuk'), left_header)
            worksheet.write(2, 7, regis_id.admission_date, bold)
            worksheet.write(1, 9, _('Tanggal Keluar'), left_header)
            worksheet.write(1, 10, regis_id.discharge_date, bold)


            # Add the worksheet data that the charts will refer to.
            headings = ['Tanggal', 'Nafas', 'Nadi', 'Suhu']
            check = ['Defecatie', 'Urine Output', 'Muntah', 'Per Oral', 'Parenteral', 'Balance']
            worksheet.write_row('A5', headings, header)
            worksheet.write_row('F5', check, header)

            row = 5

            for eval in active_id:
                x = datetime.strptime(eval['create_date'], "%Y-%m-%d %H:%M:%S")
                date_ev = x.strftime("%d %b %Y")

                worksheet.write(row, 0, date_ev)
                worksheet.write(row, 1, eval['osat'])
                worksheet.write(row, 2, eval['systolic'])
                worksheet.write(row, 3, eval['temperature'])
                row += 1

            #######################################################################

            # INJEKSI & OBAT

            injeksi = ['TANGGAL','INJEKSI']
            obat = ['TANGGAL','OBAT-OBATAN']

            worksheet.write_row('M5', injeksi, header)
            worksheet.write_row('P5', obat, header)

            order_id = self.env['sale.order'].sudo().search([('reg_id','=',self.env.context.get('active_id')), ('create_date', '>=', tglawal), ('create_date', '<=', str_end_date)])

            row_injek = 5

            for order in order_id:
                x = datetime.strptime(order['create_date'], "%Y-%m-%d %H:%M:%S")
                date_ev = x.strftime("%d %b %Y")
                
                # date SO
                worksheet.write(row_injek, 12, date_ev) 

                # Order Line Details
                order_line_id = self.env['sale.order.line'].sudo().search([('order_id','=', order.id)])
                for line in order_line_id:        
                    worksheet.write(row_injek, 13, line['name'])
                    row_injek += 1


            prescription_id = self.env['oeh.medical.prescription'].sudo().search([('reg_id','=',self.env.context.get('active_id')), ('create_date', '>=', tglawal), ('create_date', '<=', str_end_date)])

            row_injek = 5

            for pres in prescription_id:
                x = datetime.strptime(pres['create_date'], "%Y-%m-%d %H:%M:%S")
                date_ev = x.strftime("%d %b %Y")
                
                # date Prescription
                worksheet.write(row_injek, 15, date_ev) 

                # Prescription Line Details
                pres_line_id = self.env['oeh.medical.prescription.line'].sudo().search([('prescription_id','=', pres.id)])
                for line in pres_line_id:        
                    worksheet.write(row_injek, 16, line['name']['name'])
                    row_injek += 1


            ##################################################################

            # Create a new bar chart.
            #
            chart1 = workbook.add_chart({'type': 'column'})

            categori = '=Sheet1!$A$6:$A$'+str(row)+''
            value = '=Sheet1!$B$6:$B$'+str(row)+''

            # Configure the first series.
            chart1.add_series({
                'name':       '=Sheet1!$B$5',
                'categories': categori,
                'values':     value,
            })

            categori = '=Sheet1!$A$6:$A$'+str(row)+''
            value = '=Sheet1!$C$6:$C$'+str(row)+''

            # Configure the first series.
            chart1.add_series({
                'name':       '=Sheet1!$C$5',
                'categories': categori,
                'values':     value,
            })

            categori = '=Sheet1!$A$6:$A$'+str(row)+''
            value = '=Sheet1!$D$6:$D$'+str(row)+''

            # Configure the first series.
            chart1.add_series({
                'name':       '=Sheet1!$D$5',
                'categories': categori,
                'values':     value,
            })


            # Add a chart title and some axis labels.
            chart1.set_title ({'name': 'Results of sample analysis'})
            chart1.set_x_axis({'name': 'Evaluation Date'})
            chart1.set_y_axis({'name': 'Sample length'})

            # Set an Excel chart style.
            chart1.set_style(11)

            # Insert the chart into the worksheet (with an offset).
            worksheet.insert_chart('R5', chart1, {'x_offset': 25, 'y_offset': 10})

            #######################################################################


            workbook.close()
            excel_file = base64.encodestring(fp.getvalue())
            wizard.report_file = excel_file
            wizard.report_printed = True
            fp.close()

        return {
            'view_mode': 'form',
            'res_id': wizard.id,
            'res_model': 'wizard.report.observasi',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'context': self.env.context,
            'target': 'new',
        }


    # @api.multi
    # def generate_report(self):
    #     data = {
    #         'billing_periode_ids': self.billing_periode_ids.id,
    #     }

    #     # _logger.info('monthly report billing id : ',billing_periode_id)
    #     return self.env['report'].get_action([], 'paymentmodule.report_monthly_billing_template', data=data)
