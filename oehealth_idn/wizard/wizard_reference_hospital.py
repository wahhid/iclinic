import xlsxwriter
import base64
from odoo import fields, models, api
from cStringIO import StringIO
from datetime import datetime
from pytz import timezone
import pytz

class WizardReferenceHospital(models.TransientModel):
    _name = "wizard.reference.hospital"

    # @api.model
    # def default_get(self, fields_list):
    #     res = super(WizardReferenceHospital, self).default_get(fields_list)
    #     res.update({'operating_unit_id': self.env.user.default_operating_unit_id.id})

    reference_date = fields.Date('Reference Date',default=fields.Date.today, readonly=True)
    unit_administration = fields.Char('Unit Administration', size=200, required=False)
    reference_hospital = fields.Char('Reference Hospital/Clinic', size=200, required=False)
    unit_administration_internal = fields.Many2one(comodel_name='oeh.medical.physician', string='Unit Administration Internal' )
    tipe_konsul = fields.Selection([('konsul1','Mohon konsultasi satu kali'), ('konsul2','Mohon untuk rawat bersama'), ('konsul3','Mohon alih rawat')], string='Tipe Konsultasi')

    def create_reference(self):
        unit_registration_id = self.env['unit.registration'].browse(self._context.get('active_id'))
        vals = {
            'is_has_reference': True,
            'unit_administration': self.unit_administration,
            'reference_hospital': self.reference_hospital,
            'unit_administration_internal': self.unit_administration_internal.id,
            'tipe_konsul': self.tipe_konsul
        }
        unit_registration_id.write(vals)