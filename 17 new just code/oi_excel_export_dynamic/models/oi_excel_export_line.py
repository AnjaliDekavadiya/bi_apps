'''
Created on Dec 11, 2018

@author: Zuhair Hammadi
'''

from odoo import models, fields

class ReportLine(models.Model):
    _name = 'oi_excel_export.line'
    _description = 'oi_excel_export.line' 
    _order = 'sequence,id'

    report_id = fields.Many2one('oi_excel_export.config', required = True, ondelete='cascade')    
    crosstab = fields.Boolean(related='report_id.crosstab', readonly = True)
    sequence = fields.Integer()
    name = fields.Char('Header', required = True, translate = True)
    value = fields.Text()
    
    crosstabloc = fields.Selection([('row', 'Row'), ('col', 'Column'), ('value', 'Measure')], string='CrossTab Location')
    visible_condition = fields.Text()
    show_title = fields.Boolean()