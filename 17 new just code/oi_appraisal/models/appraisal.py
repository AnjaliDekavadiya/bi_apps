'''
Created on Mar 26, 2023

@author: Zuhair Hammadi
'''
from odoo import models, fields, api, _
from odoo.tools.sql import index_exists
from odoo.exceptions import AccessError

class Appraisal(models.Model):    
    _name = 'appraisal'    
    _description='Employee Appraisal'
    _inherit = ['approval.record', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char('Number', required = True, readonly = True, compute = '_calc_name', store = True, precompute = True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required = True, readonly = True, index = True)
    company_id = fields.Many2one(related='employee_id.company_id', readonly = True, store = True, precompute = True)
    
    department_id = fields.Many2one('hr.department', string='Department', compute = '_calc_employee_related', store = True, precompute = True)
    job_id = fields.Many2one('hr.job', string='Job Position', compute = '_calc_employee_related', store = True, precompute = True)
    manager_id = fields.Many2one('hr.employee', string='Manager', compute = '_calc_employee_related', store = True, precompute = True)    
    
    template_id = fields.Many2one('appraisal.template', string='Template', required = True, readonly = True)
    
    batch_id = fields.Many2one('appraisal.batch', required = True, index = True)
    phase_id = fields.Many2one('appraisal.phase')
    
    year = fields.Char(related='batch_id.year', readonly=True, store=True, precompute = True)
    
    evaluation_ids = fields.One2many('appraisal.evaluation', 'appraisal_id')
    evaluation_count = fields.Integer(compute = '_calc_evaluation_count')
    
    parent_id = fields.Many2one('appraisal', string='Manager Appraisal', compute = '_calc_parent_id', store = True)
    child_ids = fields.One2many('appraisal', 'parent_id', string='Subordinates Appraisal')
    
    comments = fields.Text()

    result = fields.Float(readonly = True, group_operator = 'avg')
    result_max = fields.Float(readonly = True, group_operator = 'avg')
    result_percent = fields.Float(readonly = True, group_operator = 'avg')
    result_title_id = fields.Many2one('appraisal.rate.line', readonly = True)
    
    objective_ids = fields.One2many('appraisal.objective', 'appraisal_id', string='Objectives', domain = [('is_ad_hoc','=', False)])
    objective_ad_hoc_ids = fields.One2many('appraisal.objective', 'appraisal_id', string='Objectives (Ad Hoc)', domain = [('is_ad_hoc','=', True)])
    parent_objective_ids = fields.One2many(related='parent_id.objective_ids', string='Manager Objectives')
    
    previous_phase_id = fields.Many2one('appraisal', compute = '_calc_previous_phase_id')
    next_phase_id = fields.Many2one('appraisal', compute = '_calc_next_phase_id')
        
    show_objectives = fields.Boolean(related='template_id.show_objectives')
    show_manager_objectives = fields.Boolean(related='template_id.show_manager_objectives')
    show_ad_hoc = fields.Boolean(related='template_id.show_ad_hoc')
    is_objectives_editable = fields.Boolean(compute = '_calc_is_objectives_editable')
            
    _sql_constraints = [
        ('batch_emp_uniq', '', 'This employee already has an appraisal on this batch!'),
    ]    
        
    def _auto_init(self):
        super()._auto_init()
        index_name = f'{self._table}_batch_emp_uniq'            
        if not index_exists(self.env.cr, index_name):
            self.env.cr.execute(f"""
                CREATE UNIQUE INDEX {index_name}
                ON {self._table}(employee_id,batch_id, COALESCE(phase_id,0));
            """)    
            
    @api.constrains('result','result_max','result_percent','result_title_id')
    def _check_result_access(self):        
        if not self.env.su and not self.env.user.has_group('oi_appraisal.group_appraisal_officer'):
            raise AccessError(_("You don't have the access rights to update the result."))    
    
    def _get_result(self, max_value = False):
        self.ensure_one()
        total_value = 0
        total_weight = 0
        for template_line in self.template_id.line_ids:
            if not template_line.weight:
                continue
            evaluation_ids = self.evaluation_ids.filtered(lambda e: e.template_line_id == template_line and e.state=='done')
            if max_value and template_line.extra:
                continue
            if not evaluation_ids:
                continue            
            value = evaluation_ids.mapped('result_max' if max_value else 'result')
            value = sum(value) / len(value) if value else 0
                        
            total_value += value * template_line.weight
            if not template_line.extra:
                total_weight += template_line.weight
            
        result = round(total_value / total_weight, 2) if total_weight else 0
        return result
    
    @api.depends('state', 'template_id.objectives_write_states', 'button_approve_enabled')
    def _calc_is_objectives_editable(self):
        for record in self:
            objectives_write_states = record.template_id.objectives_write_states or ["draft"]
            record.is_objectives_editable = record.button_approve_enabled and record.state in objectives_write_states
            
    def _calc_result(self):
        for record in self:
            if record.state not in self.template_id.result_status:
                continue
            record.result = record._get_result()
            record.result_max = record._get_result(True)
            record.result_percent = round(record.result * 100 / record.result_max,2) if record.result_max else 0

            for line in record.template_id.rating_type_id.lines_ids.sorted('value', reverse = True):
                if line.value <= record.result:
                    record.result_title_id = line
                    break
            else:
                record.result_title_id = False
                                
    def _get_link_appraisal_phase(self, direction):        
        phase_ids = self.env['appraisal.phase'].search([]).ids
        index = phase_ids.index(self.phase_id.id) if self.phase_id.id in phase_ids else False
        if index is False:
            return
        index += direction
        if index>=0 and index < len(phase_ids):
            phase_id = phase_ids[index]
            return self.search([('employee_id','=', self.employee_id.id), ('batch_id','=', self.batch_id.id),('phase_id','=', phase_id)], limit =1)
                         
    @api.depends('phase_id')
    def _calc_previous_phase_id(self):
        for record in self:
            record.previous_phase_id = record._get_link_appraisal_phase(-1)
                
    @api.depends('phase_id')
    def _calc_next_phase_id(self):
        for record in self:
            record.next_phase_id = record._get_link_appraisal_phase(1)                                                                                                 
    
    @api.depends('company_id')
    def _calc_name(self):
        for record in self:
            record.name = self.env['ir.sequence'].with_company(record.company_id.id).next_by_code(self._name)
    
    @api.depends('evaluation_ids')
    def _calc_evaluation_count(self):
        for record in self:
            record.evaluation_count = len(record.evaluation_ids)
            
    @api.depends('employee_id')
    def _calc_employee_related(self):
        for record in self:
            record.department_id = record.employee_id.department_id
            record.job_id = record.employee_id.job_id
            record.manager_id = record.employee_id.parent_id

    @api.depends('manager_id','phase_id', 'batch_id.appraisal_ids')
    def _calc_parent_id(self):              
        for record in self:
            record.parent_id = self.search([('employee_id', '=', record.manager_id.id), ('batch_id', '=', record.batch_id.id),('phase_id','=', record.phase_id.id)], limit =1)
    
    def action_view_evaluation(self):
        return {
            'type' : 'ir.actions.act_window',
            'name' : _('Evaluations'),
            'res_model' : 'appraisal.evaluation', 
            'view_mode' : 'tree,form',
            'domain' : [('appraisal_id','=', self.id)],
            'context' : {
                'default_appraisal_id' : self.id
                }
            }    
                                            
    def _create_evaluation(self):
        for record in self:
            for line in record.template_id.line_ids:
                if not line.evaluator_field_id:
                    continue
                evaluator_ids = record.employee_id[line.evaluator_field_id.name]
                for evaluator_id in evaluator_ids:
                    vals = {
                        'appraisal_id' : self.id,
                        'evaluation_template_id' : line.evaluation_template_id.id,
                        'evaluator_id' : evaluator_id.id,                        
                        }
                    domain = [(name,'=', value) for name,value in vals.items()]                    
                    if self.env['appraisal.evaluation'].search(domain):
                        continue
                    vals.update({
                        'template_line_id' : line.id
                        })
                    self.env['appraisal.evaluation'].create(vals)
                    
                    
    def _on_approval(self, old_state, new_state):
        if new_state in self.template_id.evaluation_status:
            self._create_evaluation()
            
        if new_state in self.template_id.result_status:
            self.sudo()._calc_result()            