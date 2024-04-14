'''
Created on Mar 5, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from xlsxwriter.utility import xl_cell_to_rowcol

class ReportImage(models.Model):
    _name = 'oi_excel_export.image'
    _description = 'oi_excel_export.image'

    report_id = fields.Many2one('oi_excel_export.config', required = True, ondelete='cascade')  
    name = fields.Char(required = True)  
    data = fields.Binary(attachment = True)
    cell = fields.Char(required = True, default = 'A1')
    
    offset_x = fields.Float()
    offset_y = fields.Float()
    scale_x = fields.Float(default = 1)
    scale_y = fields.Float(default = 1)
    
    @api.constrains('cell')
    def _check_cell(self):
        for record in self:
            row, col = xl_cell_to_rowcol(record.cell)
            if row<0 or col < 0:
                raise ValidationError(_('Invalid Cell'))