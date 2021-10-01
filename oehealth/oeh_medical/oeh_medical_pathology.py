# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
# [GCC 8.4.0]
# Embedded file name: D:\Workspaces\Odoo10\mod\Health\addons-comcustom\oehealth\oeh_medical\oeh_medical_pathology.py
# Compiled at: 2018-05-21 08:12:03
from odoo import api, SUPERUSER_ID, fields, models, _

class OeHealthPathologyCategory(models.Model):
    _description = 'Disease Categories'
    _name = 'oeh.medical.pathology.category'
    name = fields.Char(string='Category Name', required=True, size=128)
    parent_id = fields.Many2one('oeh.medical.pathology.category', string='Parent Category', index=True)
    child_ids = fields.One2many('oeh.medical.pathology.category', 'parent_id', string='Children Category')
    active = fields.Boolean(string='Active', default=lambda *a: 1)
    _order = 'parent_id,id'


class OeHealthPathology(models.Model):
    _name = 'oeh.medical.pathology'
    _description = 'Diseases'
    name = fields.Char(string='Disease Name', size=128, help='Disease name', required=True)
    code = fields.Char(string='Code', size=32, help='Specific Code for the Disease (eg, ICD-10, SNOMED...)')
    category = fields.Many2one('oeh.medical.pathology.category', string='Disease Category')
    chromosome = fields.Char(string='Affected Chromosome', size=128, help='chromosome number')
    protein = fields.Char(string='Protein involved', size=128, help='Name of the protein(s) affected')
    gene = fields.Char(string='Gene', size=128, help='Name of the gene(s) affected')
    info = fields.Text(string='Extra Info')
    _sql_constraints = [
     ('code_uniq', 'unique (code)', 'The disease code must be unique')]

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            tit = '(%s) %s' % (record.code, record.name)
            res.append((record.id, tit))

        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=80):
        args = args or []
        if name:
            args = ['|', ('name', operator, name), ('code', operator, name)] + args
        record = self.search(args, limit=limit)
        return record.name_get()