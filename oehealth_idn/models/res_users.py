from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DSDF, DEFAULT_SERVER_DATETIME_FORMAT



class ResUsers(models.Model):
    _inherit = 'res.users'

    default_unit_administration_id = fields.Many2one('unit.administration', 'Default Unit Administration')
    