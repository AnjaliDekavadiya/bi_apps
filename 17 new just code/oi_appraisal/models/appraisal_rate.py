'''
Created on Nov 12, 2018

@author: Zuhair Hammadi
'''
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AppraisalRate(models.Model):    
    _name = 'appraisal.rate'
    _inherit = ['appraisal.name.mixin']
    _description = 'Appraisal Rate'
    
    lines_ids = fields.One2many('appraisal.rate.line', 'rate_type_id', copy = True)    
    max_value = fields.Float('Maximum Value', compute='_get_max', store=True, readonly = False)
    type = fields.Selection([('question', 'Question Answer'),('result','Result Title')],required = True, default ='question')
    
    @api.depends('lines_ids.value')
    def _get_max(self):
        for record in self:
            values = record.mapped('lines_ids.value')
            record.max_value = values and max(values) or 0
    
    @api.constrains('lines_ids', 'max_value')
    def _check_max(self):
        for record in self:
            if record.lines_ids and record.max_value <=0:
                raise ValidationError(_('Max Value must be > 0'))
            
    