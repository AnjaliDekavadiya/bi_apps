'''
Created on Nov 12, 2018

@author: Zuhair Hammadi
'''

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AppraisalRateLine(models.Model):    
    _name = 'appraisal.rate.line'
    _description = 'Appraisal Rate Line'
    _order = 'value'
    
    name = fields.Char(required = True, translate=True)
    description = fields.Text(translate=True)
    value = fields.Float()
    rate_type_id = fields.Many2one('appraisal.rate', required = True, ondelete='cascade')
    
    value_to = fields.Float(compute = '_calc_value_to', recursive = True)
    
    _sql_constraints= [
            ('name_unqiue', 'unique(rate_type_id, name)', 'Name must be unique!')
        ]                
    
    @api.constrains('value')
    def _check_value(self):
        for record in self:
            if record.value < 0:
                raise ValidationError(_('Value must be positive'))
                    
    @api.depends('value','rate_type_id.lines_ids.value')
    def _calc_value_to(self):
        value_to = self.rate_type_id.max_value
        for record in self.rate_type_id.lines_ids.sorted(reverse = True):
            record.value_to = value_to
            value_to = record.value
            
            if value_to < self.rate_type_id.max_value:
                value_to -= 0.01
            