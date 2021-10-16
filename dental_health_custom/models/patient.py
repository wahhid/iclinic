# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DSDF, \
DEFAULT_SERVER_DATETIME_FORMAT


class oeh_medical_patient(models.Model):
    _inherit = 'oeh.medical.patient'

    @api.model
    def create(self, vals):
        res = super(oeh_medical_patient, self).create(vals)
        res.update({'name': vals['name'].title()})
        return res
