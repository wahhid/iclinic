import logging
from datetime import timedelta

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.http import request

_logger = logging.getLogger(__name__)

class medical_evaluation_patient(models.Model):
    _inherit = 'oeh.medical.physician'

    is_doctor = fields.Boolean(string='Is Doctor ?')
    physician_position = fields.Char(string='Position')
    