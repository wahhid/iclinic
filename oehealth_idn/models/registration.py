# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
# [GCC 8.4.0]
# Embedded file name: D:\Workspaces\Odoo10\mod\Health\addons-custom\oehealth_idn\models\registration.py
# Compiled at: 2018-12-12 15:45:33
from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
import datetime, requests, json
import logging


_logger = logging.getLogger(__name__)

class register_walkin(models.Model):
    _inherit = 'oeh.medical.appointment.register.walkin'
    
    PAYMENT_TYPE = [
     ('Personal', 'Personal'),
     ('Corporate', 'Corporate'),
     ('Insurance', 'Insurance'),
     ('Employee', 'Employee')
    ]

    WALKIN_STATUS = [
     ('Draft', 'Draft'),
     ('Scheduled', 'Scheduled'),
     ('Completed', 'Completed'),
     ('Invoiced', 'Invoiced'),
     ('Cancelled', 'Cancelled')]

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            tit = '%s / %s' % (record.name, record.patient.name)
            res.append((record.id, tit))

        return res

    # @api.model
    # def default_get(self, fields_list):
    #     res = super(register_walkin, self).default_get(fields_list)
    #     res.update({'operating_unit_id': self.env.user.default_operating_unit_id.id})

    @api.model
    def find_payment_guarantor_discount(self):
        if self.payment == 'Personal':
            #Personal
            domain = [
                ('payment','=', 'Personal')
            ]
            payment_quarantor_discount_id = self.env['payment.guarantor.discount'].search(domain, limit=1)
            if not payment_quarantor_discount_id:
                raise  Warning(_('Payment Guarantor Discount not found'))
            self.payment_quarantor_discount_id = payment_quarantor_discount_id
        elif self.payment == 'Corporate':
            #Corporate
            _logger.info('Corporate')
            domain = [
                ('payment','=', 'Corporate'),
                ('company','=', self.company.id)
            ]
            _logger.info(domain)
            payment_guarantor_discount_id = self.env['payment.guarantor.discount'].search(domain, limit=1)
            if not payment_guarantor_discount_id:
                _logger.info('Payment Guarantor not found!')
                # warning_mess = {
                #         'title': _('Payment Guarantor Discount'),
                #         'message': 'Payment Guarantor Discount not found'
                # }
                # return {'warning': warning_mess}
                raise Warning(_('Payment Guarantor Discount not found'))
            _logger.info('Description')
            _logger.info(payment_guarantor_discount_id.description)
            self.payment_guarantor_discount_id = payment_guarantor_discount_id.id
        elif self.payment == 'Insurance':
            #Insurance
            _logger.info('Insurance')
            domain = [
                ('payment','=', 'Insurance'),
                ('insurance_type_id','=', self.insurance.ins_type.id)
            ]
            _logger.info(domain)
            payment_guarantor_discount_id = self.env['payment.guarantor.discount'].search(domain, limit=1)
            if not payment_guarantor_discount_id:
                raise Warning(_('Payment Guarantor Discount not found'))
            _logger.info(payment_guarantor_discount_id.description)
            self.payment_guarantor_discount_id = payment_guarantor_discount_id.id
        else:
            #Employee
            domain = [
                ('payment','=', 'Employee')
            ]
            payment_quarantor_discount_id = self.env['payment.guarantor.discount'].search(domain, limit=1)
            if not payment_quarantor_discount_id:
                raise Warning(_('Payment Guarantor Discount not found'))
            self.payment_quarantor_discount_id = payment_quarantor_discount_id.id

    @api.onchange('insurance')
    def onchange_for_insurance(self):
        _logger.info("On Change Insurance")
        self.find_payment_guarantor_discount()

    @api.onchange('company')
    def onchange_for_company(self):
        _logger.info("On Change Company")
        self.find_payment_guarantor_discount()

    @api.onchange('employee_id')
    def onchange_for_employee(self):
        _logger.info("On Change Employee")
        self.find_payment_guarantor_discount()



    clinic_ids = fields.One2many(comodel_name='unit.registration', inverse_name='clinic_walkin_id', string='Out-Patient Registration', readonly=True, states={'Scheduled': [('readonly', False)]}, track_visibility='onchange')
    unit_ids = fields.One2many(comodel_name='unit.registration', inverse_name='unit_walkin_id', string='In-Patient Registration', readonly=True, states={'Scheduled': [('readonly', False)]}, track_visibility='onchange')
    emergency_ids = fields.One2many(comodel_name='unit.registration', inverse_name='emergency_walkin_id', string='Emergency Registration', readonly=True, states={'Scheduled': [('readonly', False)]}, track_visibility='onchange')
    support_ids = fields.One2many(comodel_name='unit.registration', inverse_name='support_walkin_id', string='Medical Support Registration', readonly=True, states={'Scheduled': [('readonly', False)]}, track_visibility='onchange')
    lab_test_ids = fields.One2many(comodel_name='oeh.medical.lab.test', inverse_name='walkin', string='Lab Test Registration', readonly=True, states={'Scheduled': [('readonly', False)]}, track_visibility='onchange')
    payment = fields.Selection(PAYMENT_TYPE, string='Payment Guarantor', default='Personal', readonly=True, states={'Scheduled': [('readonly', False)]}, track_visibility='onchange')
    company = fields.Many2one(comodel_name='res.partner', string='Company', readonly=True, states={'Scheduled': [('readonly', False)]}, track_visibility='onchange')
    insurance = fields.Many2one(comodel_name='medical.insurance', string='Insurance', readonly=True, states={'Scheduled': [('readonly', False)]}, track_visibility='onchange')
    employee_id = fields.Many2one('oeh.medical.patient', 'Employee', readonly=True)
    payment_guarantor_discount_id = fields.Many2one('payment.guarantor.discount', 'Payment Guarantor Discount', readonly=False)
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', default=lambda self: self.env.user.default_operating_unit_id.id)
    unit = fields.Many2one(comodel_name='unit.administration', string='Unit', track_visibility='onchange')
    admission_reason = fields.Many2one('oeh.medical.pathology', string='Reason for Admission', help='Reason for Admission', required=False, readonly=True, states={'Scheduled': [('readonly', False)]}, track_visibility='onchange')
    have_register = fields.Boolean(string='Have Register ?')
    is_blacklist = fields.Boolean(related='patient.is_blacklist')
    queue_trans_id = fields.Many2one('queue.trans','Queue')
    state = fields.Selection(WALKIN_STATUS, string='State', readonly=True, states={'Scheduled': [('readonly', False)]}, default=lambda *a: 'Draft')

    @api.model
    def create(self, vals):
        vals['state'] = 'Scheduled'
        if 'payment_guarantor_discount_id' in vals:
            vals.update({'payment_guarantor_discount_id': vals.get('payment_guarantor_discount_id')})
        count = self.env['oeh.medical.appointment.register.walkin'].search([('patient', '=', vals['patient']), ('state', '=', 'Scheduled')])
        if count:
            raise Warning('The patient already has an active registration! \n Please Check Arrival ID # ' + count.name)
        
        return super(register_walkin, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'payment_guarantor_discount_id' in vals:
            vals.update({'payment_guarantor_discount_id': vals.get('payment_guarantor_discount_id')})
        return super(register_walkin, self).write(vals)

    @api.onchange('patient', 'dob')
    def check_registration(self):
        count = self.env['oeh.medical.appointment.register.walkin'].search([('patient', '=', self.patient.id), ('state', '=', 'Scheduled')])
        #self.insurance = self.patient.current_insurance.id
        if count:
            raise Warning('The patient already has an active registration! \n Please Check Arrival ID # ' + count.name)

    @api.multi
    def set_to_completed(self):
        if not self.clinic_ids and not self.unit_ids and not self.emergency_ids and not self.support_ids:
            raise UserError(_('Completed Failed! \n Registration Line empty !'))
        else:
            for line in self.clinic_ids:
                if line.state in 'Unlock':
                    raise UserError(_('Out-Patient Care! \n Reg ID # ' + line.name + ' must be lock first !'))

            for line in self.unit_ids:
                if line.state in 'Unlock':
                    raise UserError(_('In-Patient Care! \n Reg ID # ' + line.name + ' must be lock first !'))

            for line in self.emergency_ids:
                if line.state in 'Unlock':
                    raise UserError(_('Emergency Care! \n Reg ID # ' + line.name + ' must be lock first !'))

            for line in self.support_ids:
                if line.state in 'Unlock':
                    raise UserError(_('Medical Support! \n Reg ID # ' + line.name + ' must be lock first !'))

            return self.write({'state': 'Completed'})

    @api.multi
    def set_to_cancelled(self):
        if not self.clinic_ids and not self.unit_ids and not self.emergency_ids and not self.support_ids:
            return self.write({'state': 'Cancelled'})
        raise UserError(_('Cancelled Failed! \n Registration not empty !'))

    @api.multi
    def unlink(self):
        if self.clinic_ids or self.unit_ids or self.emergency_ids or self.support_ids:
            raise UserError(_('Deleted Failed! \n Registration not empty !'))
        return super(register_walkin, self).unlink()

    @api.multi
    def print_patient_stiker(self):
        return self.patient.print_patient_stiker()


    @api.multi
    def onchange_patient(self, patient):
        if patient:  
            # is_has_parent = False
            # domain = [('family_patient_id', '=', patient)]
            # family_patient_id = self.env['oeh.medical.patient.family'].search(domain,limit=1)
            # if family_patient_id:
            #     is_has_parent = True
            #     parent_id = family_patient_id.patient_id
            
            patient = self.env['oeh.medical.patient'].browse(patient)
            if patient.is_employee:
                return {
                    'value': {
                        'dob': patient.dob, 
                        'sex': patient.sex, 
                        'marital_status': patient.marital_status, 
                        'blood_type': patient.blood_type, 
                        'rh': patient.rh,
                        'payment': 'Insurance',
                        'insurance': patient.current_insurance.id
                    },
                    'warning': {
                        'title': _('Warning'),
                        'message': _('This Pasien is employee')
                    }
                }
            elif patient.is_have_parent:
                _logger.info(patient.parent_id.current_insurance.id)
                return {
                    'value': {
                        'dob': patient.dob, 
                        'sex': patient.sex, 
                        'marital_status': patient.marital_status, 
                        'blood_type': patient.blood_type, 
                        'rh': patient.rh,
                        'payment': 'Insurance',
                        'insurance': patient.parent_id.current_insurance.id
                    },
                    'warning': {
                        'title': _('Warning'),
                        'message': _('This Pasien have relation with employee (' + patient.parent_id.name + ')')
                    }
                }
            else:
                return {
                    'value': {
                        'dob': patient.dob, 
                        'sex': patient.sex, 
                        'marital_status': patient.marital_status, 
                        'blood_type': patient.blood_type, 
                        'rh': patient.rh,
                        'payment': 'Personal',
                        'insurance': False,
                        'company': False,
                        'employee_id': False
                    }
                }
        return {}
