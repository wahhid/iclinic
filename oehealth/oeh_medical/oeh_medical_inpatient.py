# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
# [GCC 8.4.0]
# Embedded file name: D:\DEV\Workspaces\odoo10\addons_custom\oehealth\oeh_medical\oeh_medical_inpatient.py
# Compiled at: 2017-10-14 16:33:18
from odoo import api, fields, models, _
import datetime
from odoo import tools
from datetime import date
from odoo.exceptions import UserError

class OeHealthInpatient(models.Model):
    _name = 'oeh.medical.inpatient'
    _description = 'Information about the Patient administration'
    ADMISSION_TYPE = [
     ('Routine', 'Routine'),
     ('Maternity', 'Maternity'),
     ('Elective', 'Elective'),
     ('Urgent', 'Urgent'),
     ('Emergency', 'Emergency'),
     ('Other', 'Other')]
    INPATIENT_STATES = [
     ('Draft', 'Draft'),
     ('Hospitalized', 'Hospitalized'),
     ('Invoiced', 'Invoiced'),
     ('Discharged', 'Discharged'),
     ('Cancelled', 'Cancelled')]

    @api.multi
    def _get_physician(self):
        """Return default physician value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain, limit=1)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    name = fields.Char(string='Inpatient #', size=128, readonly=True, required=True, default=lambda *a: '/')
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help='Patient Name', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    admission_type = fields.Selection(ADMISSION_TYPE, string='Admission Type', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    admission_reason = fields.Many2one('oeh.medical.pathology', string='Reason for Admission', help='Reason for Admission', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    admission_date = fields.Datetime(string='Hospitalization Date', readonly=True, states={'Draft': [('readonly', False)]})
    discharge_date = fields.Datetime(string='Discharge Date', readonly=False, states={'Discharged': [('readonly', True)]})
    attending_physician = fields.Many2one('oeh.medical.physician', string='Attending Physician', readonly=False, states={'Discharged': [('readonly', True)]}, default=_get_physician)
    operating_physician = fields.Many2one('oeh.medical.physician', string='Operating Physician', readonly=False, states={'Discharged': [('readonly', True)]})
    ward = fields.Many2one('oeh.medical.health.center.ward', string='Ward', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    bed = fields.Many2one('oeh.medical.health.center.beds', string='Bed', required=True, readonly=True, states={'Draft': [('readonly', False)]})
    nursing_plan = fields.Text(string='Nursing Plan', readonly=False, states={'Discharged': [('readonly', True)]})
    discharge_plan = fields.Text(string='Discharge Plan', readonly=False, states={'Discharged': [('readonly', True)]})
    admission_condition = fields.Text(string='Condition before Admission', readonly=True, states={'Draft': [('readonly', False)]})
    info = fields.Text(string='Extra Info', readonly=False, states={'Discharged': [('readonly', True)]})
    state = fields.Selection(INPATIENT_STATES, string='State', default=lambda *a: 'Draft')

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('oeh.medical.inpatient')
        vals['name'] = sequence or '/'
        health_inpatient = super(OeHealthInpatient, self).create(vals)
        return health_inpatient

    @api.multi
    def _default_account(self):
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        return journal.default_credit_account_id.id

    @api.multi
    def set_to_hospitalized(self):
        hospitalized_date = False
        bed_obj = self.env['oeh.medical.health.center.beds']
        for ina in self:
            if ina.admission_date:
                hospitalized_date = ina.admission_date
            else:
                hospitalized_date = datetime.datetime.now()
            if ina.bed:
                query = _("update oeh_medical_health_center_beds set state='Occupied' where id=%s") % str(ina.bed.id)
                self.env.cr.execute(query)

        return self.write({'state': 'Hospitalized', 'admission_date': hospitalized_date})

    @api.multi
    def set_to_discharged(self):
        discharged_date = False
        bed_obj = self.env['oeh.medical.health.center.beds']
        for ina in self:
            if ina.discharge_date:
                discharged_date = ina.discharge_date
            else:
                discharged_date = datetime.datetime.now()
            if ina.bed:
                query = _("update oeh_medical_health_center_beds set state='Free' where id=%s") % str(ina.bed.id)
                self.env.cr.execute(query)

        return self.write({'state': 'Discharged', 'discharge_date': discharged_date})

    @api.multi
    def set_to_invoiced(self):
        invoice_obj = self.env['account.invoice']
        invoice_line_obj = self.env['account.invoice.line']
        inv_ids = []
        res = {}
        for inpatient in self:
            duration = 1
            if inpatient.admission_date and inpatient.discharge_date:
                admission_date = datetime.datetime.strptime(inpatient.admission_date, '%Y-%m-%d %H:%M:%S')
                discharge_date = datetime.datetime.strptime(inpatient.discharge_date, '%Y-%m-%d %H:%M:%S')
                delta = date(discharge_date.year, discharge_date.month, discharge_date.day) - date(admission_date.year, admission_date.month, admission_date.day)
                if delta.days == 0:
                    duration = 1
                else:
                    duration = delta.days
            if inpatient.bed:
                curr_invoice = {'partner_id': inpatient.patient.partner_id.id, 'account_id': inpatient.patient.partner_id.property_account_receivable_id.id, 
                   'patient': inpatient.patient.id, 
                   'state': 'draft', 
                   'type': 'out_invoice', 
                   'date_invoice': datetime.datetime.now(), 
                   'origin': 'Inpatient# : ' + inpatient.name, 
                   'target': 'new'}
                inv_ids = invoice_obj.create(curr_invoice)
                prd_account_id = self._default_account()
                curr_invoice_line = {'name': 'Inpatient Admission charge for ' + str(duration) + ' day(s) of ' + inpatient.bed.product_id.name, 
                   'product_id': inpatient.bed.product_id.id, 
                   'price_unit': duration * inpatient.bed.list_price, 
                   'quantity': 1.0, 
                   'account_id': prd_account_id, 
                   'invoice_id': inv_ids.id}
                inv_line_ids = invoice_line_obj.create(curr_invoice_line)
                res = self.write({'state': 'Invoiced'})
            else:
                raise UserError(_('Please first select bed to raise an invoice !'))

        return res

    @api.multi
    def set_to_cancelled(self):
        bed_obj = self.env['oeh.medical.health.center.beds']
        for ina in self:
            if ina.bed:
                query = _("update oeh_medical_health_center_beds set state='Free' where id=%s") % str(ina.bed.id)
                self.env.cr.execute(query)

        return self.write({'state': 'Cancelled'})

    @api.multi
    def set_to_draft(self):
        return self.write({'state': 'Draft'})


class OeHealthInpatientProfile(models.Model):
    _name = 'oeh.medical.inpatient.mydetails'
    _description = 'Patient view only own admissions'
    _auto = False
    INPATIENT_STATES = [
     ('Draft', 'Draft'),
     ('Hospitalized', 'Hospitalized'),
     ('Invoiced', 'Invoiced'),
     ('Discharged', 'Discharged'),
     ('Cancelled', 'Cancelled')]
    name = fields.Char(string='Inpatient #', size=128, readonly=True)
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help='Patient Name', readonly=True)
    admission_type = fields.Char(string='Admission Type', size=128, readonly=True)
    admission_reason = fields.Many2one('oeh.medical.pathology', string='Reason for Admission', help='Reason for Admission', readonly=True)
    admission_date = fields.Datetime(string='Hospitalization Date', readonly=True)
    discharge_date = fields.Datetime(string='Discharge Date', readonly=True)
    attending_physician = fields.Many2one('oeh.medical.physician', string='Attending Physician', readonly=True)
    operating_physician = fields.Many2one('oeh.medical.physician', string='Operating Physician', readonly=True)
    ward = fields.Many2one('oeh.medical.health.center.ward', string='Ward', required=True, readonly=True)
    bed = fields.Many2one('oeh.medical.health.center.beds', string='Bed', required=True, readonly=True)
    nursing_plan = fields.Text(string='Nursing Plan', readonly=True)
    discharge_plan = fields.Text(string='Discharge Plan', readonly=True)
    admission_condition = fields.Text(string='Condition before Admission', readonly=True)
    info = fields.Text(string='Extra Info', readonly=True)
    state = fields.Selection(INPATIENT_STATES, string='State', readonly=True)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'oeh_medical_inpatient_mydetails')
        self.env.cr.execute('\n            create or replace view oeh_medical_inpatient_mydetails as (\n                 select\n                     o.id as id,\n                     o.name as name,\n                     o.patient as patient,\n                     o.admission_type as admission_type,\n                     o.admission_date as admission_date,\n                     o.admission_reason as admission_reason,\n                     o.discharge_date as discharge_date,\n                     o.attending_physician as attending_physician,\n                     o.operating_physician as operating_physician,\n                     o.ward as ward,\n                     o.bed as bed,\n                     o.nursing_plan as nursing_plan,\n                     o.discharge_plan as discharge_plan,\n                     o.admission_condition as admission_condition,\n                     o.info as info,\n                     o.state as state\n                 from\n                     oeh_medical_inpatient o\n            )\n        ')