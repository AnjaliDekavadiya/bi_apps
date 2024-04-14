'''
Created on Sep 8, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields, api
from odoo.tools.convert import safe_eval

class Job(models.Model):
    _inherit = "hr.job"
    
    attribute_value_ids = fields.One2many('hr.attribute.value', 'job_id', string='Attributes', domain=['|',('active','=',False),('active','=',True)])
    attribute_count = fields.Integer(compute = '_calc_attribute_count')
    
    @api.depends('attribute_value_ids')
    def _calc_attribute_count(self):
        for record in self:
            record.attribute_count = len(record.attribute_value_ids.filtered('isactive'))
        
    def action_attribute(self):
        action, = self.env.ref('oi_contract_attribute.act_hr_attribute_value').read()
        action['domain'] = [('job_id','=', self.id)]
        context = safe_eval(action.get('context') or '{}')
        context['default_job_id'] = self.id
        action['context'] = context
        action['views'] = [(self.env.ref('oi_contract_attribute.view_hr_attribute_value_tree_job').id, 'tree'), (self.env.ref('oi_contract_attribute.view_hr_attribute_value_form_job').id, 'form')]
        return action