from odoo import models, fields, api, _
from odoo.exceptions import UserError

class inherit_medical_evaluation(models.Model):
    _inherit = 'oeh.medical.evaluation'
    
    subjective = fields.Text(string='Subjective')
    allergy_history = fields.Text(string='Allergy History')
    diagnostic_ids = fields.One2many(comodel_name='oeh.multi.diagnostic', inverse_name='eval_id', string='Diagnostic')