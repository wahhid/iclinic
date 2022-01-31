from odoo import fields
import datetime
from odoo.exceptions import except_orm
from dateutil.relativedelta import relativedelta
try:
    from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
except ImportError:
    class ReportXlsx(object):
        def __init__(self, *args, **kwargs):
            pass


class ProjectReportXlsx(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, objects):
        sheet1 = "Project plan"
        sheet2 = "Notes"
        worksheet1 = workbook.add_worksheet(sheet1)
        worksheet2 = workbook.add_worksheet(sheet2)
        format_main_header = workbook.add_format({'font_size': 14, 'bg_color': 'silver', 'bold': 1, 'border': 1,
                                                  'align': 'center', 'valign': 'vcenter'})
        format_header = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center',
                                             'valign': 'vcenter', 'bg_color': 'silver'})
        header = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center',
                                      'valign': 'vcenter', 'bg_color': 'silver'})
        left_header = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center',
                                           'valign': 'vcenter'})
        format_cell = workbook.add_format({'border': 1, 'align': 'center'})


        # # ---------------------Bar chart for Time duration-------------------------- #
        chart_bar_t = workbook.add_chart({'type': 'bar'})
        actual_time = planned_time = 10
        # for data in task:
        #     if data.planned_hours:
        #         planned_time += data.planned_hours
        #     actual_time += data.effective_hours

        data_bar_t = [
            ['Planned time', 'Actual time'],
            [planned_time, actual_time],
        ]
        col = 6
        row = 0
        worksheet2.merge_range(row, col, row + 1, col + 3, "Time Duration(Hours)", header)
        row += 2
        for item in range(2):
            worksheet2.merge_range(row, col, row, col + 1, data_bar_t[0][item], format_cell)
            col += 2
            worksheet2.merge_range(row, col, row, col + 1, data_bar_t[1][item], format_cell)
            col = 6
            row += 1
        chart_bar_t.add_series({'name': 'Time',
                                'categories': '=' + sheet2 + '!$G$3:$G$4',
                                'values': '=' + sheet2 + '!$I$3:$I$4',
                                })
        chart_bar_t.set_title({'name': 'Time Duration'})
        worksheet1.insert_chart('I13', chart_bar_t)

    ProjectReportXlsx('report.obserpasi_terapi_patient_report', 'unit.registration')