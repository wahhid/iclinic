# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
# [GCC 8.4.0]
# Embedded file name: D:\DEV\Workspaces\odoo10\addons_custom\oehealth\oeh_medical\oeh_medical_genetics.py
# Compiled at: 2017-10-14 16:33:18
from odoo import fields, models

class OeHealthGenetics(models.Model):
    _name = 'oeh.medical.genetics'
    _description = 'Information about the genetics risks'
    DOMINANCE = [
     ('Dominant', 'Dominant'),
     ('Recessive', 'Recessive')]
    name = fields.Char(string='Official Symbol', size=16)
    long_name = fields.Char(string='Official Long Name', size=256)
    gene_id = fields.Char(string='Gene ID', size=8, help='Default code from NCBI Entrez database.')
    chromosome = fields.Char(string='Affected Chromosome', size=2, help='Name of the affected chromosome')
    location = fields.Char(string='Location', size=32, help='Locus of the chromosome')
    dominance = fields.Selection(DOMINANCE, string='Dominance', index=True)
    info = fields.Text(string='Information', size=128, help='Name of the protein(s) affected')