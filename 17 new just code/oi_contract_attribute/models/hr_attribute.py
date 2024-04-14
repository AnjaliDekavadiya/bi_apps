'''
Created on Oct 30, 2018

@author: Zuhair Hammadi
'''
from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError

class HRAttribute(models.Model):
    _name = 'hr.attribute'
    _description='Employee Attribute'
    _order = 'name'
    
    name = fields.Char(required = True)
    code = fields.Char(required = True)      
    active = fields.Boolean(default = True)
    
    type = fields.Selection([('int', 'Integer'), ('float', 'Number'), ('str', 'Text')], required = True, string='Type')
    valid_to_required = fields.Boolean('Valid To Required')
        
    selection_ids = fields.One2many('hr.attribute.selection', 'attribute_id', string='Available Values')    
    # selection_id = fields.Many2one('hr.attribute.selection',  string='Available Value')
    has_selection = fields.Boolean(compute = '_calc_has_selection', store = True)
    
    contract = fields.Boolean()
    contracts = fields.Boolean('Contracts Selection')
    grade = fields.Boolean()
    job = fields.Boolean('Job Position')
    department = fields.Boolean()
    schedule = fields.Boolean()
    category = fields.Boolean('Contract Type')
    company = fields.Boolean()
    step = fields.Boolean()
    
    value_ids = fields.One2many('hr.attribute.value', 'attribute_id')
    value_count = fields.Integer(compute = '_calc_value_count')    
    
    contract_type_ids = fields.Many2many('hr.contract.type', string ='Contract Types')
    
    required_approval = fields.Boolean('Required Approval')
    
    value_type = fields.Selection([('positive', 'Positive'), ('negative', 'Negative')], string = "Value Type")
    field_to_update_id = fields.Many2one('ir.model.fields')
    
    _sql_constraints = [
        ('uk_name', 'unique(name)', 'Name must be unique!'),
        ('uk_code', 'unique(code)', 'Code must be unique!')
        ]
    
    def _sync_field_values(self):
        today = fields.Date.today()
        for record in self.env['hr.attribute'].sudo().search([]).filtered('field_to_update_id'):
            updated_contract_ids = self.env['hr.contract']
            for value in record.value_ids:
                if value.valid_from <= today and (not value.valid_to or value.valid_to < today):
                    contract_domain = [('state','in',['draft'])]
                    if self.env.context.get('employee_id'):
                        employee_id = record.env.context.get('employee_id')
                        contract_domain.extend([('employee_id','=',employee_id)])
                        
                    for option, domain in [('contract', [('id','=', value.contract_id.id or 0)]),   
                             ('contracts', [('id','in', value.contract_ids.ids or [0])]),                               
                              ('job', [('job_id','=', value.job_id.id or 0)]),
                              ('step', [('step_id','=', value.step_id.id or 0)]),
                              ('grade', [('grade_id','=', value.grade_id.id or 0)]),
                              ('department', [('department_id','=', value.department_id.id or 0)]),
                              ('schedule', [('schedule_id','=', value.schedule_id.id or 0), ('grade_id','=', False)]),
                              ('category', [('category_id','=', value.category_id.id or 0)]),
                              ('company', [('company_id','=', value.employee_id.company_id.id or 0)]),
                              ]:
                        
                        if record[option]:
                            contract_domain.extend(domain)
                    contract_ids = self.env['hr.contract'].search(contract_domain)
                    contract_ids.with_context(from_attr_sync  = True).write({record.field_to_update_id.name : value.selection_id.name})
                    updated_contract_ids += contract_ids
                
            
    @api.depends('value_ids')
    def _calc_value_count(self):
        for record in self:
            record.value_count = len(record.value_ids)
    
    @api.depends('selection_ids')
    def _calc_has_selection(self):
        for record in self:
            record.has_selection = bool(record.selection_ids)
            
    def _get_opposite_value_type(self, value_type):
        return 'negative' if value_type == 'positive' else 'positive'
            
    @api.constrains('value_type', 'selection_ids', 'value_ids')     
    def _check_value_type(self):
        for record in self:
            value_type = record.value_type
            opposite_value_type = self._get_opposite_value_type(value_type)
            if record.type in ['int', 'float']:
                for value in record.selection_ids.mapped('name'):
                    if (value_type == 'positive' and float(value) < 0) or (value_type == 'negative' and float(value) > 0):
                        raise ValidationError("Value type is {} but one or more of the values is {}".format(value_type, opposite_value_type))
                    
                for value in record.value_ids.mapped('value'):
                    if (value_type == 'positive' and float(value) < 0) or (value_type == 'negative' and float(value) > 0):
                        raise ValidationError("One or more related records to this attribute has a {} value while the value type is {}".format(opposite_value_type, value_type))
    
    
    @api.constrains('type', 'selection_ids')     
    def _check_selection_ids(self):
        for record in self:
            for value in record.mapped('selection_ids.name'):
                try:
                    record._get_value(value)
                except Exception as e:
                    raise ValidationError(str(e))                    
    
    def _get_value(self, value):
        if not self:
            return
        func = safe_eval(self.type)        
        if not value:
            return func()
        return func(value)    
    
    def get_selection(self, convert = True):
        res= self.selection_ids.mapped('name')
        if convert:
            func = safe_eval(self.type)
            res = list(map(func,res))
        return res
    
    def action_values(self):
        self.ensure_one()
        action, = self.env.ref('oi_contract_attribute.act_hr_attribute_value').read()
        context = safe_eval(action.get('context') or '{}')
        context.update( {
            'default_attribute_id' : self.id
            })
        action['context'] = context
        action['domain'] = [('attribute_id','=', self.id)]
        return action