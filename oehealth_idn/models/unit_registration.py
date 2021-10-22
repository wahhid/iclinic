# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
# [GCC 8.4.0]
# Embedded file name: D:\Workspaces\Odoo10\mod\Health\addons-klinik-online\oehealth_idn\models\unit_registration.py
# Compiled at: 2019-07-28 17:50:56
from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
import requests, json, datetime
from datetime import timedelta
import pytz
import logging

_logger = logging.getLogger(__name__)

class unit_registration(models.Model):
    _name = 'unit.registration'
    _inherit = ['mail.thread']
    _order = 'name desc'
    
    PAYMENT_TYPE = [
        ('Personal', 'Personal'),
        ('Corporate', 'Corporate'),
        ('Insurance', 'Insurance'),
        ('Employee', 'Employee')
    ]
    CLINIC_STATUS = [
     ('Draft', 'Draft'),
     ('Unlock', 'Unlock'),
     ('Lock', 'Lock'),
     ('Done', 'Done'),
     ('Check-In', 'Check-In'),
     ('Check-Out', 'Check-Out'),
     ('Cancelled', 'Cancelled')]
    QUEUE_STATUS = [
     ('Waiting', 'Waiting'),
     ('Now', 'Now'),
     ('Done', 'Done')]

    @api.onchange('unit')
    def change_unit(self):
        for row in self:
            row.doctor = ''

    @api.onchange('room_id')
    def get_charge_id(self):
        for row in self:
            row.charge_id = row.room_id.class_id

    @api.onchange('class_id')
    def change_class_id(self):
        for row in self:
            row.room_id = ''
            row.charge_id = ''
            row.charge_id = ''
            row.bed = ''

    @api.onchange('patient')
    def get_insurance(self):
        pass
        # for row in self:
        #     row.insurance = row.patient.current_insurance

    name = fields.Char(string='Reg ID #', required=True, readonly=True, default=lambda *a: '/')
    queue = fields.Char(string='Queue #', compute='get_queue', readonly=True)
    queue_no = fields.Integer(string='Queue No.', readonly=True)
    patient = fields.Many2one(comodel_name='oeh.medical.patient', string='Patient', help='Patient Name', required=True, readonly=True, states={'Draft': [('readonly', False)]}, track_visibility='onchange')
    is_blacklist = fields.Boolean(related='patient.is_blacklist')
    dob = fields.Date(string='Date of Birth', related='patient.dob', store=True)
    age = fields.Char(related='patient.age')
    type = fields.Selection([('Out-Patient', 'Out-Patient'),
     ('In-Patient', 'In-Patient'),
     ('Emergency', 'Emergency'),
     ('Medical Support', 'Medical Support'),
     ('Logistic', 'Logistic'),
     ('Non-Medis', 'Non-Medis')], 'Unit Type', readonly=True, states={'Draft': [('readonly', False)]})
    unit = fields.Many2one(comodel_name='unit.administration', string='Unit', readonly=True, states={'Draft': [('readonly', False)]}, track_visibility='onchange')
    doctor = fields.Many2one(comodel_name='oeh.medical.physician', string='Doctor', readonly=True, states={'Draft': [('readonly', False)]}, track_visibility='onchange')
    payment = fields.Selection(PAYMENT_TYPE, string='Payment Guarantor', default='Personal', readonly=True, states={'Draft': [('readonly', False)]}, track_visibility='onchange')
    company = fields.Many2one(comodel_name='res.partner', string='Company', readonly=True, states={'Draft': [('readonly', False)]}, track_visibility='onchange')
    insurance = fields.Many2one(comodel_name='medical.insurance', string='Insurance', readonly=True, states={'Draft': [('readonly', False)]}, track_visibility='onchange')
    employee_id = fields.Many2one('oeh.medical.patient', 'Employee', readonly=True)
    payment_guarantor_discount_id = fields.Many2one('payment.guarantor.discount', 'Payment Guarantor Discount')
    remarks = fields.Text(string='Remarks', readonly=True, states={'Unlock': [('readonly', False)]}, track_visibility='onchange')
    reference_id = fields.Many2one(comodel_name='unit.registration', string='Reference ID', readonly=True, states={'Draft': [('readonly', False)], 'Unlock': [('readonly', False)]}, track_visibility='onchange')
    doctor_reference = fields.Many2one(comodel_name='oeh.medical.physician', related='reference_id.doctor', string='Doctor Reference', help='Doctor Reference', readonly=True)
    schedule = fields.Selection([('No', 'Not Appointment'), ('Yes', 'Appointment')], string='Schedule', default='No', readonly=True, states={'Unlock': [('readonly', False)]}, track_visibility='onchange')
    date = fields.Datetime(string='Date', default=fields.Datetime.now(), readonly=True, states={'Draft': [('readonly', False)]}, track_visibility='onchange')
    class_id = fields.Many2one(comodel_name='class.administration', readonly=True, states={'Draft': [('readonly', False)]}, string='Class Name')
    room_id = fields.Many2one(comodel_name='oeh.medical.health.center.ward', readonly=True, states={'Draft': [('readonly', False)]}, string='Room Name')
    charge_id = fields.Many2one(comodel_name='class.administration', string='Charge Type', readonly=True, states={'Draft': [('readonly', False)]}, track_visibility='onchange')
    bed = fields.Many2one(comodel_name='oeh.medical.health.center.beds', readonly=True, states={'Draft': [('readonly', False)]}, string='Bed')
    admission_date = fields.Datetime(string='Check-In Date', readonly=True, states={'Unlock': [('readonly', False)]}, track_visibility='onchange')
    admission_condition = fields.Text(string='Condition before Admission', readonly=True, states={'Unlock': [('readonly', False)]}, track_visibility='onchange')
    admission_reason = fields.Many2one('oeh.medical.pathology', string='Reason for Admission', help='Reason for Admission', required=False, readonly=True, states={'Unlock': [('readonly', False)]}, track_visibility='onchange')
    discharge_date = fields.Datetime(string='Check-Out Date', readonly=True, states={'Unlock': [('readonly', False)]}, track_visibility='onchange')
    discharge_plan = fields.Text(string='Discharge Plan', readonly=True, states={'Unlock': [('readonly', False)]}, track_visibility='onchange')
    nursing_plan = fields.Text(string='Nursing Plan', readonly=True, states={'Unlock': [('readonly', False)]}, track_visibility='onchange')
    extra_info = fields.Text(string='Extra Information', readonly=True, states={'Unlock': [('readonly', False)]}, track_visibility='onchange')
    is_control = fields.Boolean(string='Next Control ?', help='Next Control ?', readonly=True, states={'Unlock': [('readonly', False)]}, default=True, track_visibility='onchange')
    control_date = fields.Datetime(string='Date Control', readonly=True, states={'Unlock': [('readonly', False)]}, track_visibility='onchange')
    request_id = fields.Many2one(comodel_name='product.product', string='Requested Services', readonly=True, states={'Draft': [('readonly', False)], 'Unlock': [('readonly', False)]}, track_visibility='onchange')
    is_medical_record = fields.Boolean(related='patient.is_medical_record', string='Is Medical Record ?', readonly=True)
    clinic_walkin_id = fields.Many2one(comodel_name='oeh.medical.appointment.register.walkin', string='Clinic Walkin')
    unit_walkin_id = fields.Many2one(comodel_name='oeh.medical.appointment.register.walkin', string='Unit Walkin')
    emergency_walkin_id = fields.Many2one(comodel_name='oeh.medical.appointment.register.walkin', string='Emergency Walkin')
    support_walkin_id = fields.Many2one(comodel_name='oeh.medical.appointment.register.walkin', string='Support Walkin')

    arrival_id = fields.Many2one(comodel_name='oeh.medical.appointment.register.walkin', compute='set_arrival_id', string='Arrival ID #')
    arrival_txt = fields.Char(compute='set_arrival_id', string='Arrival #')
    sale_ids = fields.One2many(comodel_name='sale.order', inverse_name='reg_id', string='Transactions')
    diagnostic_ids = fields.One2many(comodel_name='oeh.multi.diagnostic', inverse_name='reg_id', string='Diagnostic')
    state = fields.Selection(CLINIC_STATUS, string='State', default='Draft', track_visibility='onchange')
    queue_state = fields.Selection(QUEUE_STATUS, string='Queue State', default='Waiting', copy=False, readonly=True, track_visibility='onchange')
    _sql_constraints = [
     ('full_name_uniq', 'unique (name)', 'The Queue Number must be unique')]

    @api.one
    def set_arrival_id(self):
        self.arrival_id = self.clinic_walkin_id.id or self.unit_walkin_id.id or self.emergency_walkin_id.id or self.support_walkin_id.id
        if not self.arrival_id:
            sequence = self.env['ir.sequence'].next_by_code('dummy_arrival')
            self.arrival_txt = '%s / %s' % (sequence, self.patient.name)

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('unit.registration')
        vals['name'] = sequence
        vals['state'] = 'Unlock'
        self.env.cr.execute("\n                            SELECT\n                                MAX(s.queue_no) AS no_max \n                            FROM\n                                unit_registration s\n                            WHERE\n                                to_char ( s.create_date, 'YYYY-MM-DD' ) = to_char ( CURRENT_DATE, 'YYYY-MM-DD' )\n                                AND s.type = %s AND s.unit = %s AND s.doctor = %s\n                            ", (vals['type'], vals['unit'], vals['doctor']))
        get_no_max = self.env.cr.dictfetchall()
        queue_no = 1
        for data in get_no_max:
            if data['no_max']:
                queue_no = int(data['no_max']) + 1
        vals['queue_no'] = queue_no
        res = super(unit_registration, self).create(vals)
        if res.payment == 'Personal':
            #Personal
            domain = [
                ('payment','=', 'Personal')
            ]
            payment_quarantor_discount_id = self.env['payment.guarantor.discount'].search(domain, limit=1)
            if not payment_quarantor_discount_id:
                raise UserError(_('Payment Guarantor Discount not found'))
            res.payment_quarantor_discount_id = payment_quarantor_discount_id
        elif res.payment == 'Corporate':
            #Corporate
            _logger.info('Corporate')
            domain = [
                ('payment','=', 'Corporate'),
                ('company','=', res.company.id)
            ]
            _logger.info(domain)
            payment_guarantor_discount_id = self.env['payment.guarantor.discount'].search(domain, limit=1)
            if not payment_guarantor_discount_id:
                raise UserError(_('Payment Guarantor Discount not found'))
            _logger.info(payment_guarantor_discount_id.description)
            res.payment_guarantor_discount_id = payment_guarantor_discount_id.id
        elif res.payment == 'Insurance':
            #Insurance
            _logger.info('Insurance')
            domain = [
                ('payment','=', 'Insurance'),
                ('insurance_type_id','=', res.insurance.ins_type.id)
            ]
            _logger.info(domain)
            payment_guarantor_discount_id = self.env['payment.guarantor.discount'].search(domain, limit=1)
            if not payment_guarantor_discount_id:
                raise UserError(_('Payment Guarantor Discount not found'))
            _logger.info(payment_guarantor_discount_id.description)
            res.payment_guarantor_discount_id = payment_guarantor_discount_id.id
        else:
            #Employee
            domain = [
                ('payment','=', 'Employee')
            ]
            payment_quarantor_discount_id = self.env['payment.guarantor.discount'].search(domain, limit=1)
            if not payment_quarantor_discount_id:
                raise UserError(_('Payment Guarantor Discount not found'))
            res.payment_quarantor_discount_id = payment_quarantor_discount_id.id

        return res

    def get_queue(self):
        for row in self:
            if row.queue_no:
                x = '00' + str(row.queue_no - 1)
                doctor_code = 0
                if row.doctor.queue_code:
                    doctor_code = '/' + str(row.doctor.queue_code)
                queue_format = str(row.unit.code) + str(doctor_code) + '/' + str(int(x) + 1).zfill(len(x))
                row.queue = queue_format

    @api.multi
    def create_reference(self):
        return {'name': 'Transactions', 
           'view_type': 'form', 
           'view_mode': 'form', 
           'res_model': 'unit.registration', 
           'type': 'ir.actions.act_window', 
           'target': 'new', 
           'context': {'default_reference_id': self.id, 
                       'default_clinic_walkin_id': self.clinic_walkin_id.id, 
                       'default_unit_walkin_id': self.unit_walkin_id.id, 
                       'default_emergency_walkin_id': self.emergency_walkin_id.id, 
                       'default_support_walkin_id': self.support_walkin_id.id, 
                       'default_patient': self.patient.id, 
                       'default_type': 'Medical Support', 
                       'default_payment': self.payment, 
                       'default_company': self.company.id, 
                       'default_insurance': self.insurance.id, 
                       'default_doctor': self.doctor.id}}

    @api.multi
    def create_sale(self):
        obj = self.env['sale.order']
        line_obj = self.env['sale.order.line']
        inv_ids = []
        guarantor = 0
        arrival = 0
        for acc in self:
            if acc.patient:
                if acc.payment == 'Insurance':
                    guarantor = acc.insurance.ins_type.partner_id.id
                elif acc.payment == 'Corporate':
                    guarantor = acc.company.id
                elif acc.payment == 'Employee':
                    guarantor = acc.employee_id.current_insurance.ins_type.partner_id.id
                else:
                    guarantor = acc.patient.partner_id.id

                val_obj = {
                    'reg_id': acc.id, 
                    'arrival_id': acc.clinic_walkin_id.id or acc.unit_walkin_id.id or acc.emergency_walkin_id.id or acc.support_walkin_id.id, 
                    'patient_id': acc.patient.id, 
                    'doctor_id': acc.doctor.id, 
                    'partner_id': acc.patient.partner_id.id, 
                    'partner_invoice_id': guarantor, 
                    'payment_guarantor_discount_id': acc.payment_guarantor_discount_id.id, 
                    'partner_shipping_id': acc.patient.partner_id.id, 
                    'pricelist_id': acc.charge_id.pricelist.id or acc.patient.partner_id.property_product_pricelist.id, 
                    'location_id': self.env['stock.location'].search([('unit_ids.operating_id', '=', self.env.user.default_operating_unit_id.id)], limit=1).id, 
                    'operating_unit_id': acc.unit.operating_id.id or False
                }
                #Create Sale Order
                inv_ids = obj.create(val_obj)

                if inv_ids:
                    inv_id = inv_ids.id
                    if self.arrival_id and not self.arrival_id.have_register:
                        product = self.env['product.product'].search([('auto_billing', '!=', False)])
                        for product_id in product:
                            discount = 0.0
                            if acc.payment_guarantor_discount_id:
                                if product_id.item_type == 'General Item':
                                    discount = acc.payment_guarantor_discount_id.general_item
                                elif product_id.item_type == 'Medical Item':        
                                    discount = acc.payment_guarantor_discount_id.medical_item
                                elif product_id.item_type == 'Food Item':        
                                    discount = acc.payment_guarantor_discount_id.food_item
                                elif product_id.item_type == 'Medicine':        
                                    discount = acc.payment_guarantor_discount_id.medicine
                                elif product_id.item_type == 'Doctor':        
                                    discount = acc.payment_guarantor_discount_id.doctor
                                elif product_id.item_type == 'Nurse':        
                                    discount = acc.payment_guarantor_discount_id.nurse
                            vals = {
                                'order_id': inv_id, 
                                'product_id': product_id.id, 
                                'name': product_id.name, 
                                'product_uom_qty': 1, 
                                'product_uom': product_id.uom_id.id, 
                                'price_unit': product_id.lst_price,
                                'discount_type': 'percent',
                                'discount': discount or False,
                                'doctor_id': False
                            }
                            #create sale order line
                            line_obj.create(vals)
                        
                        #Set Have Register Status
                        arrival = self.env['oeh.medical.appointment.register.walkin'].browse(self.arrival_id.id)
                        arrival.write({'have_register': True})
            else:
                raise UserError(_('Configuration error! \n Could not find any patient to create the transactions !'))

        return {'name': 'Transactions', 'view_type': 'form', 
           'view_mode': 'form', 
           'res_id': inv_id, 
           'res_model': 'sale.order', 
           'type': 'ir.actions.act_window'}

    @api.multi
    def view_sale(self):
        tree_view_id = self.env.ref('oehealth_idn.sale_order_health_tree_view').id
        form_view_id = self.env.ref('sale.view_order_form').id
        return {
            'domain': "[('reg_id','=', " + str(self.id) + ')]', 
           'name': 'Transactions', 
           'view_type': 'form', 
           'view_mode': 'tree,form', 
           'views': [
                    [
                    tree_view_id, 'tree'],
                   [
                    form_view_id, 'form']], 
           'res_model': 'sale.order', 
           'type': 'ir.actions.act_window'}

    def set_lock(self):
        if self.type == 'In-Patient':
            if self.is_control and not self.control_date:
                raise UserError(_('Locking Error! \n Date Control must be set !'))
        if not self.sale_ids:
            raise UserError(_('Locking Error! \n Transaction empty !'))
        for line in self.sale_ids:
            if line.state not in ('sale', 'done'):
                raise UserError(_('Locking Error! \n Transaction # ' + line.name + ' must be confirm first !'))
            else:
                self.write({'state': 'Lock'})

    def set_unlock(self):
        self.write({'state': 'Unlock'})

    def set_now(self):
        for row in self:
            self.env.cr.execute("\n                                UPDATE\n                                    unit_registration\n                                SET\n                                    queue_state = 'Done'\n                                WHERE\n                                    doctor = %s AND id != %s AND queue_state = 'Now'\n                                ", (row.doctor.id, row.id))
            self.queue_state = 'Now'

        return {'type': 'ir.actions.client', 
           'tag': 'reload'}

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
                query = _("update oeh_medical_health_center_beds set state='Occupied', reg_id=%s where id=%s") % (str(ina.id), str(ina.bed.id))
                self.env.cr.execute(query)

        return self.write({'state': 'Check-In', 'admission_date': hospitalized_date})

    @api.multi
    def create_sale_charge_bed(self):
        obj = self.env['sale.order']
        line_obj = self.env['sale.order.line']
        inv_ids = []
        guarantor = 0
        arrival = 0
        for acc in self:
            if acc.patient:
                if acc.payment == 'Insurance':
                    guarantor = acc.insurance.ins_type.partner_id.id
                elif acc.payment == 'Corporate':
                    guarantor = acc.company.id
                else:
                    guarantor = acc.patient.partner_id.id
                val_obj = {'reg_id': acc.id, 
                   'arrival_id': acc.clinic_walkin_id.id or acc.unit_walkin_id.id or acc.emergency_walkin_id.id or acc.support_walkin_id.id, 
                   'patient_id': acc.patient.id, 
                   'doctor_id': acc.doctor.id, 
                   'partner_id': acc.patient.partner_id.id, 
                   'partner_invoice_id': guarantor, 
                   'partner_shipping_id': acc.patient.partner_id.id, 
                   'pricelist_id': acc.charge_id.pricelist.id or acc.patient.partner_id.property_product_pricelist.id, 
                   'location_id': self.env['stock.location'].search([('unit_ids.operating_id', '=', self.env.user.default_operating_unit_id.id)], limit=1).id}
                inv_ids = obj.create(val_obj)
                if inv_ids:
                    inv_id = inv_ids.id
                    if self.arrival_id and not self.arrival_id.have_register:
                        product = self.env['product.product'].search([('auto_billing', '!=', False)])
                        for p in product:
                            vals = {'order_id': inv_id, 'product_id': p.id, 
                               'name': p.name, 
                               'product_uom_qty': 1, 
                               'product_uom': p.uom_id.id, 
                               'price_unit': p.lst_price, 
                               'doctor_id': False}
                            line_obj.create(vals)

                        arrival = self.env['oeh.medical.appointment.register.walkin'].browse(self.arrival_id.id)
                        arrival.write({'have_register': True})
                    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
                    tz = pytz.timezone(self.env.user.partner_id.tz) or pytz.utc
                    date_in = pytz.utc.localize(datetime.datetime.strptime(acc.admission_date, DATETIME_FORMAT)).astimezone(tz)
                    date_now = pytz.utc.localize(datetime.datetime.now(), DATETIME_FORMAT).astimezone(tz)
                    if acc.discharge_date:
                        date_out = pytz.utc.localize(datetime.datetime.strptime(acc.discharge_date, DATETIME_FORMAT)).astimezone(tz)
                    else:
                        date_out = date_now
                    diff = date_out - date_in
                    days = diff.days
                    hours = int(diff.seconds // 3600)
                    days = days + int(hours / 12)
                    qty_charge = days or 1
                    vals_bed = {'order_id': inv_id, 
                       'product_id': acc.bed.product_id.id, 
                       'name': acc.bed.name, 
                       'product_uom_qty': qty_charge, 
                       'product_uom': acc.bed.product_id.uom_id.id, 
                       'price_unit': acc.bed.list_price, 
                       'doctor_id': acc.doctor.id}
                    line_obj.create(vals_bed)
            else:
                raise UserError(_('Configuration error! \n Could not find any patient to create the transactions !'))

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
                ina.create_sale_charge_bed()
                query = _("update oeh_medical_health_center_beds set state='Free', reg_id=NULL where id=%s") % str(ina.bed.id)
                self.env.cr.execute(query)

        return self.write({'state': 'Check-Out', 'discharge_date': discharged_date})

    @api.multi
    def set_to_cancelled(self):
        bed_obj = self.env['oeh.medical.health.center.beds']
        for ina in self:
            if ina.bed:
                query = _("update oeh_medical_health_center_beds set state='Free', reg_id=NULL where id=%s") % str(ina.bed.id)
                self.env.cr.execute(query)

        return self.write({'state': 'Cancelled'})