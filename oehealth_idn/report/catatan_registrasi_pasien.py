from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
import logging


_logger = logging.getLogger(__name__)

class ReportCatatanRegistrasi(models.AbstractModel):
    _name = 'report.oehealth_idn.report_catatan_registrasi_pasien'

    @api.model
    def _get_report_values(self, walkin_id=False, patient=False):
        records = {}

        walkin = self.env['oeh.medical.appointment.register.walkin'].sudo().search([('id','=', walkin_id)])
        reg_id = False

        if len(walkin.clinic_ids) > 0:
            bol = False
            for ffe in walkin.clinic_ids:
                if bol == False:
                    reg_id = ffe.id
                    bol = True 

        if len(walkin.unit_ids) > 0:
            bol = False
            for ffe in walkin.unit_ids:
                if bol == False:
                    reg_id = ffe.id
                    bol = True 

        if len(walkin.emergency_ids) > 0:
            bol = False
            for ffe in walkin.emergency_ids:
                if bol == False:
                    reg_id = ffe.id
                    bol = True 

        if len(walkin.support_ids) > 0:
            bol = False
            for ffe in walkin.support_ids:
                if bol == False:
                    reg_id = ffe.id
                    bol = True 
            
        
        registration_id = self.env['unit.registration'].sudo().search([('id','=', reg_id)])
        
        records.update({'docs': registration_id}) 

        
        evaluation_ids = self.env['oeh.medical.evaluation'].sudo().search([('reg_id','=', registration_id.id)], order='create_date desc')
        lab_ids = self.env['oeh.medical.lab.test'].sudo().search([('reg_id','=', registration_id.id)], order='create_date desc')
        imaging_ids = self.env['oeh.medical.imaging'].sudo().search([('reg_id','=', registration_id.id)], order='create_date desc')
        
        evaluation_list = []
        for ev in evaluation_ids:
            _logger.info(ev.doctor.is_doctor)
            # if ev.doctor.is_doctor == 'True':
            pathology_list = []
            for diag in ev.diagnostic_ids:
                pathology_list.append({
                    'pathology': diag.name
                })


            evaluation_list.append({
                'name': ev.name,
                'date': ev.evaluation_start_date,
                'is_nurse' : ev.doctor.is_nurse,
                'is_doctor': ev.doctor.is_doctor,
                'notes_complaint': ev.notes_complaint,
                'notes': ev.notes,
                'subjective': ev.subjective,
                'tujuan': ev.tujuan,
                'resiko': ev.resiko,
                'komplikasi': ev.komplikasi,
                'alternatif': ev.alternatif,
                'systolic': ev.systolic,
                'diastolic': ev.diastolic,
                'temperature': ev.temperature,
                'nadi': ev.nadi,
                'respiratory_rate': ev.respiratory_rate,
                'osat': ev.osat,
                'gcs_e': ev.gcs_e,
                'gcs_v': ev.gcs_v,
                'gcs_m': ev.gcs_m,
                'total_gcs': ev.total_gcs,
                'gds': ev.gds,
                'pathology_list': pathology_list 
            })

                
        records.update({'evaluation_list': evaluation_list})

        lab_list = []
        for lab in lab_ids:
            lab_list.append({
                'name': lab.name
            })
        records.update({'lab_list': lab_list})

        imaging_list = []
        for imag in imaging_ids:
            imaging_list.append({
                'name': imag.name
            })
        records.update({'imaging_list': imaging_list})

        # TINDAKAN
        sale_order_list = []
        sale_order_ids = self.env['sale.order'].sudo().search([('reg_id','=', registration_id.id)])
        for order in sale_order_ids:
            sale_order_line_ids = self.env['sale.order.line'].sudo().search([('order_id','=', order.id)])

            for line in sale_order_line_ids:
                date_order = order.date_order

                if line.product_id.type == 'service':
                    vals = {
                        'tanggal': date_order,
                        'tindakan' : line.name,
                        'doctor_name': order.doctor_id.name,
                    }
                    sale_order_list.append(vals)

        records.update({'sale_order_list': sale_order_list}) 

        
        prescription_ids = self.env['oeh.medical.prescription'].sudo().search([('reg_id','=', registration_id.id)], order='create_date desc')
        
        prescription_list = []
        for pres in prescription_ids:
            list_obat = []
            for pres_line in pres.prescription_line:
                list_obat.append({
                    'common_dosage': pres_line.common_dosage.name,
                    'name': pres_line.name.name,
                    'dose_route': pres_line.dose_route.name
                })

            prescription_list.append({
                'nomor': pres.name,
                'list_obat': list_obat
            })


        _logger.info("===PRESCRIPTION")        
        _logger.info(prescription_list)

        records.update({'prescription_list': prescription_list}) 

        return records

    @api.multi
    def render_html(self, docids, data=None):
        _logger.info("Render Report")
        _logger.info(str(data['walkin']))
        data = dict(data or {})
        medis = self._get_report_values(data['walkin'])
        _logger.info('WALKIN ID ===')
        _logger.info(medis)
        data.update(medis)
        return self.env['report'].render('oehealth_idn.report_catatan_registrasi_pasien', data)