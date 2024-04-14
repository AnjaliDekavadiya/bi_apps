'''
Created on Apr 11, 2023

@author: Zuhair Hammadi
'''
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AppraisalEvaluation(models.Model):    
    _name = 'appraisal.evaluation'
    _description = 'Appraisal Evaluation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Number', required = True, readonly = True, compute = '_calc_name', store = True, precompute = True)
    appraisal_id = fields.Many2one('appraisal', required = True, index = True, readonly = True)
    batch_id = fields.Many2one(related='appraisal_id.batch_id', store = True, precompute = True)
    phase_id = fields.Many2one(related='appraisal_id.phase_id', store = True, precompute = True)
    company_id = fields.Many2one(related='appraisal_id.company_id', readonly = True, store = True, precompute = True)
    employee_id = fields.Many2one(related='appraisal_id.employee_id', store = True, precompute = True)
    department_id = fields.Many2one(related='appraisal_id.department_id', store = True, precompute = True)
    
    template_line_id = fields.Many2one('appraisal.template.line', string='Evaluator Type', required = True, readonly = True)
    evaluation_template_id = fields.Many2one('appraisal.evaluation.template', required = True, readonly = True)
    evaluator_id = fields.Many2one('hr.employee', required = True, readonly = True)
    
    active = fields.Boolean(default = True, tracking=True)    
    
    line_ids = fields.One2many('appraisal.evaluation.line', 'evaluation_id')
    
    data = fields.Json(compute = '_calc_data', inverse ='_inverse_data')
    
    result = fields.Float(compute = '_calc_result', store = True, group_operator = 'avg')
    result_max = fields.Float(compute = '_calc_result', store = True, group_operator = 'avg')
    result_percent = fields.Float(compute = '_calc_result', store = True, group_operator = 'avg')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Completed'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
        
    @api.depends('company_id')
    def _calc_name(self):
        for record in self:
            record.name = self.env['ir.sequence'].with_company(record.company_id.id).next_by_code(self._name)
                
    def _get_result(self, max_value = False):
        self.ensure_one()
        total_value = 0
        total_weight = 0
        
        for template_line in self.evaluation_template_id.line_ids:
            if not template_line.weight:
                continue           
            question_group_id = template_line.question_group_id
            if not question_group_id.question_ids and not question_group_id.question_type.startswith('rating'):
                continue                    
        
            if max_value:
                value = question_group_id.rating_type_id.max_value
            else:
                if question_group_id.question_type == 'rating_objectives':
                    evaluation_lines = self.line_ids.filtered(lambda line: line.objective_id)
                else:
                    evaluation_lines = self.line_ids.filtered(lambda line: line.question_id.question_group_id == question_group_id)
                evaluation_lines = evaluation_lines.filtered(lambda line: line.value or not line.optional)
                
                value_t = 0
                weight_t = 0
                for line in evaluation_lines:
                    value_t += line.value_float * line.weight
                    weight_t += line.weight
                
                value = value_t / weight_t if weight_t else 0    
            
            total_value += value * template_line.weight
            total_weight += template_line.weight            
        
        return round(total_value / total_weight,2) if total_weight else 0                    
    
    @api.depends('line_ids.value_float', 'state')
    def _calc_result(self):
        for record in self:                
            record.result = record._get_result()
            record.result_max = record._get_result(True)
            record.result_percent = round(record.result * 100 / record.result_max,2) if record.result_max else 0
    
    def _inverse_data(self):
        def set_value(question_id, value, is_objective):
            fname = 'objective_id' if  is_objective else 'question_id'
            line_id = self.line_ids.filtered(lambda line: line[fname].id == question_id)
            vals = {'value' : value}
            if not line_id:
                vals.update({
                    'evaluation_id' : self.id,
                    fname : question_id
                    })
                line_id = self.line_ids.create(vals)
            else:
                line_id.write(vals)
                
            line_id._recompute_value()
        
        for group in self.data['groups']:
            for line in group['lines']:
                set_value(line['id'], line.get('value'), group.get('is_objective'))        
    
    @api.depends('line_ids')
    def _calc_data(self):
        for record in self:
            data = {
                'groups' : [],
                'has_lines': bool(record.line_ids)
                }
            for template_line in record.evaluation_template_id.line_ids:
                question_group_id = template_line.question_group_id
                group = {
                    'id' : question_group_id.id,
                    'name' : question_group_id.name,
                    'description' : question_group_id.description,
                    'type' : question_group_id.question_type,
                    'lines' : [],
                    'is_objective' : question_group_id.question_type == 'rating_objectives',
                    'weight' : template_line.weight
                    }
                if question_group_id.question_type.startswith('rating'):
                    group['rating'] = [
                        {'value' : line.value, 'name' : line.name, 'description' : line.description}
                        for line in question_group_id.rating_type_id.lines_ids
                        ]
                
                if question_group_id.question_type == 'rating_objectives':
                    for objective in record.appraisal_id.objective_ids:
                        evaluation_line = record.line_ids.filtered(lambda line: line.objective_id == objective)
                        vals = {
                            'id' : objective.id,
                            'name' : objective.name,
                            'description': objective.description,
                            'value' : evaluation_line.value,
                            'is_section' : bool(objective.display_type)
                            }                        
                        group['lines'].append(vals)
                else:                
                    for question in question_group_id.question_ids:
                        evaluation_line = record.line_ids.filtered(lambda line: line.question_id == question)
                        if question.computed and not evaluation_line:
                            value = evaluation_line._compute_value(record, question)
                        else:
                            value = evaluation_line.value
                        vals = {
                            'id' : question.id,
                            'name' : question.name,
                            'description': question.description,
                            'value' : value,
                            'widget' : question.widget,
                            'optional' : question.optional,
                            'computed' : question.computed
                            }
                        if question.widget in ['selection', 'radio']:
                            vals['selection'] = [(selection.name, selection.name) for selection in question.selection_ids]
                        group['lines'].append(vals) 
                
                data['groups'].append(group)                            
                
            record.data = data            
            
    def action_done(self):
        if not self.line_ids:
            raise UserError(_("Please answer all required evaluation questions"))        
        for line in self.line_ids:
            if not line.value and not line.optional:
                raise UserError(_("Please answer all required evaluation questions"))        
            
        self.state='done'
        
    @api.ondelete(at_uninstall=False)
    def _unlink_except_done(self):
        for record in self:
            if record.state =='done':
                raise UserError(_('You cannot delete completed evaluation'))
