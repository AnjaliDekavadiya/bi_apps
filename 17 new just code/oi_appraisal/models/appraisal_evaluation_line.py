'''
Created on Apr 26, 2023

@author: Zuhair Hammadi
'''
from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval

class AppraisalEvaluationLine(models.Model):    
    _name = 'appraisal.evaluation.line'
    _description = 'Appraisal Evaluation Line'
    
    evaluation_id = fields.Many2one('appraisal.evaluation', required = True, ondelete='cascade', index = True)
    question_id = fields.Many2one('appraisal.question')
    objective_id = fields.Many2one('appraisal.objective')
    
    optional = fields.Boolean(compute ='_calc_optional')
    weight = fields.Float(compute = '_calc_weight')

    value = fields.Char()
    value_float = fields.Float(compute = '_calc_value_float', store = True, precompute = True)
    
    _sql_constraints = [
        ('check1', 'check(question_id is null or objective_id is null)', 'Evaluation Line must be link to either question or objective'),
        ('check2', 'check(question_id is not null or objective_id is not null)', 'Evaluation Line must be link to either question or objective'),
    ]    

    @api.depends('value')    
    def _calc_value_float(self):
        for record in self:
            try:
                record.value_float = float(record.value)
            except ValueError:
                record.value_float = 0
                    
    @api.depends('question_id.weight', 'objective_id.weight')
    def _calc_weight(self):
        for record in self:
            record.weight = record.question_id.weight or record.objective_id.weight
            
    
    @api.depends('question_id.optional', 'objective_id.display_type')       
    def _calc_optional(self):
        for record in self:
            if record.question_id:
                record.optional = record.question_id.optional
            else:
                record.optional = record.objective_id.display_type == 'line_section'
                                
    def _compute_value(self, evaluation, question):
        if not question.compute_code:
            return
        locals_dict = self.env['ir.actions.actions']._get_eval_context()
        locals_dict.update({
            'evaluation' : evaluation,
            'employee' : evaluation.employee_id,
            'appraisal' : evaluation.appraisal_id
            })
        safe_eval(question.compute_code.strip(), locals_dict=locals_dict, mode='exec', nocopy=True)
        return locals_dict.get('result')
    
    def _recompute_value(self):                      
        if self.question_id.computed:
            self.value = self._compute_value(self.evaluation_id, self.question_id)