from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date
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


    # @api.model
    # def get_observasi_details(self):
    #     """ Serialise the orders of the day information
    #     params: date_start, date_stop string representing the datetime of order
    #     """

    #     monthlybilling = self.env['billing.periode'].search([
    #         ('id', '=', self.billing_periode_ids.id), ])

    #     _logger.info(monthlybilling)

    #     monthlybilling_datas = []

    #     for billing in monthlybilling:

    #         for line in billing.line_ids:
    #             vals = {}
    #             vals.update({'unitno': line.unitno})
    #             vals.update({'date_trans': line.date_trans})
    #             vals.update({'description': line.description})
    #             vals.update({'amount': line.amount})

    #             monthlybilling_datas.append(vals)

    #     return {
    #         "monthlybilling": monthlybilling_datas
    #     }


    reg_id = fields.Many2one(comodel_name="unit.registration", string="Reg.Id", required=True,)
    report_filename = fields.Char('Filename', size=100, readonly=True, default='ObservasiReport.xlsx')
    report_file = fields.Binary('File', readonly=True)
    report_printed = fields.Boolean('Report Printed', default=False, readonly=True)

    @api.multi
    def generate_report_excel(self):
        for wizard in self:
            sheet1 = "Observasi"
            sheet2 = "Notes"

            fp = StringIO()
            workbook = xlsxwriter.Workbook(fp)
            # column_heading_style = easyxf('font:height 200;font:bold True;')

            # # request_details = self.get_billing_details()
            # worksheet = workbook.add_worksheet('Observasi Report')
            # worksheet.write(0, 0, _('UNIT #'))
            # worksheet.write(0, 1, _('DATE'))
            # worksheet.write(0, 2, _('DESCRIPTION'))
            # worksheet.write(0, 3, _('AMOUNT'))
            # row = 1
            # for order in request_details['monthlybilling']:
            #     worksheet.write(row, 0, order['unitno'])
            #     worksheet.write(row, 1, order['date_trans'])
            #     worksheet.write(row, 2, order['description'])
            #     worksheet.write(row, 3, order['amount'])
            #     row += 1

            # format_main_header = workbook.add_format({'font_size': 14, 'bg_color': 'silver', 'bold': 1, 'border': 1,
            #                                         'align': 'center', 'valign': 'vcenter'})
            # format_header = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center',
            #                                     'valign': 'vcenter', 'bg_color': 'silver'})
            # header = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center',
            #                             'valign': 'vcenter', 'bg_color': 'silver'})
            # left_header = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center',
            #                                 'valign': 'vcenter'})
            # format_cell = workbook.add_format({'border': 1, 'align': 'center'})


            # # # ---------------------Bar chart for Time duration-------------------------- #
            # chart_bar_t = workbook.add_chart({'type': 'bar'})
            # actual_time = planned_time = 10
            # # for data in task:
            # #     if data.planned_hours:
            # #         planned_time += data.planned_hours
            # #     actual_time += data.effective_hours

            # data_bar_t = [
            #     ['Planned time', 'Actual time'],
            #     [planned_time, actual_time],
            # ]
            # col = 6
            # row = 0
            # worksheet.merge_range(row, col, row + 1, col + 3, "Time Duration(Hours)", header)
            # row += 2
            # for item in range(2):
            #     worksheet.merge_range(row, col, row, col + 1, data_bar_t[0][item], format_cell)
            #     col += 2
            #     worksheet.merge_range(row, col, row, col + 1, data_bar_t[1][item], format_cell)
            #     col = 6
            #     row += 1
            # chart_bar_t.add_series({'name': 'Time',
            #                         'categories': '=' + sheet2 + '!$G$3:$G$4',
            #                         'values': '=' + sheet2 + '!$I$3:$I$4',
            #                         })
            # chart_bar_t.set_title({'name': 'Time Duration'})
            # worksheet.insert_chart('I13', chart_bar_t)

            # workbook = xlsxwriter.Workbook('chart_line.xlsx')

            active_id = self.env['oeh.medical.evaluation'].search([('reg_id','=',self.env.context.get('active_id'))])

            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': 1})

            # Add the worksheet data that the charts will refer to.
            headings = ['Tanggal', 'Nafas', 'Nadi', 'Suhu']
            # data = [
            #     [2, 3, 4, 5, 6, 7],
            #     [10, 40, 50, 20, 10, 50],
            #     [30, 60, 70, 50, 40, 30],
            # ]

            worksheet.write_row('A5', headings, bold)
            # worksheet.write_column('A2', data[0])
            # worksheet.write_column('B2', data[1])
            # worksheet.write_column('C2', data[2])

            # worksheet.write(0, 0, _('UNIT #'))
            # worksheet.write(0, 1, _('DATE'))
            # worksheet.write(0, 2, _('DESCRIPTION'))
            # worksheet.write(0, 3, _('AMOUNT'))
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
            #
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

            # Configure a second series. Note use of alternative syntax to define ranges.
            # chart1.add_series({
            #     'name':       ['Sheet1', 0, 2],
            #     'categories': ['Sheet1', 1, 0, 6, 0],
            #     'values':     ['Sheet1', 1, 2, 6, 2],
            # })

            # Add a chart title and some axis labels.
            chart1.set_title ({'name': 'Results of sample analysis'})
            chart1.set_x_axis({'name': 'Evaluation Date'})
            chart1.set_y_axis({'name': 'Sample length'})

            # Set an Excel chart style.
            chart1.set_style(11)

            # Insert the chart into the worksheet (with an offset).
            worksheet.insert_chart('D2', chart1, {'x_offset': 25, 'y_offset': 10})

            #######################################################################
            #
            # Create a stacked chart sub-type.
            #
            # chart2 = workbook.add_chart({'type': 'bar', 'subtype': 'stacked'})

            # # Configure the first series.
            # chart2.add_series({
            #     'name':       '=Sheet1!$B$1',
            #     'categories': '=Sheet1!$A$2:$A$7',
            #     'values':     '=Sheet1!$B$2:$B$7',
            # })

            # # Configure second series.
            # chart2.add_series({
            #     'name':       '=Sheet1!$C$1',
            #     'categories': '=Sheet1!$A$2:$A$7',
            #     'values':     '=Sheet1!$C$2:$C$7',
            # })

            # # Add a chart title and some axis labels.
            # chart2.set_title ({'name': 'Stacked Chart'})
            # chart2.set_x_axis({'name': 'Test number'})
            # chart2.set_y_axis({'name': 'Sample length (mm)'})

            # # Set an Excel chart style.
            # chart2.set_style(12)

            # # Insert the chart into the worksheet (with an offset).
            # worksheet.insert_chart('D18', chart2, {'x_offset': 25, 'y_offset': 10})

            # #######################################################################
            # #
            # # Create a percentage stacked chart sub-type.
            # #
            # chart3 = workbook.add_chart({'type': 'bar', 'subtype': 'percent_stacked'})

            # # Configure the first series.
            # chart3.add_series({
            #     'name':       '=Sheet1!$B$1',
            #     'categories': '=Sheet1!$A$2:$A$7',
            #     'values':     '=Sheet1!$B$2:$B$7',
            # })

            # # Configure second series.
            # chart3.add_series({
            #     'name':       '=Sheet1!$C$1',
            #     'categories': '=Sheet1!$A$2:$A$7',
            #     'values':     '=Sheet1!$C$2:$C$7',
            # })

            # # Add a chart title and some axis labels.
            # chart3.set_title ({'name': 'Percent Stacked Chart'})
            # chart3.set_x_axis({'name': 'Test number'})
            # chart3.set_y_axis({'name': 'Sample length (mm)'})

            # # Set an Excel chart style.
            # chart3.set_style(13)

            # # Insert the chart into the worksheet (with an offset).
            # worksheet.insert_chart('D34', chart3, {'x_offset': 25, 'y_offset': 10})

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
