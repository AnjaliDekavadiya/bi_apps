'''
Created on Oct 30, 2018

@author: Zuhair Hammadi
'''
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ContractAttribute(models.Model):
    _name= 'hr.attribute.value'
    _description='Employee Attribute Value'
    _order = 'active desc,valid_from desc,id desc'
    _rec_name = 'employee_id'
        
    attribute_id = fields.Many2one('hr.attribute', string='Attribute', required = True, index = True)
    type = fields.Selection(related='attribute_id.type', readonly = True)
    code = fields.Char(related='attribute_id.code', readonly = True)  
    has_selection = fields.Boolean(related='attribute_id.has_selection', readonly = True)
    
    active = fields.Boolean(default = True)
    valid_from = fields.Date('Valid From', required = True, default = fields.Date.today)
    valid_to = fields.Date('Valid To')
    
    value = fields.Char(compute = '_compute_value')
    selection_id = fields.Many2one('hr.attribute.selection', string='Value')
    
    isactive = fields.Boolean(compute = '_calc_isactive', string='Current Value', search='_search_isactive')
    
    valid_to_required = fields.Boolean(related='attribute_id.valid_to_required', readonly = True)
    
    contract_id = fields.Many2one('hr.contract', string='Contract', index = True, ondelete = 'cascade')
    contract_ids = fields.Many2many('hr.contract', string='Contracts')
    employee_id = fields.Many2one(related='contract_id.employee_id', readonly = True, store = True)
    grade_id = fields.Many2one('hr.salary.grade', ondelete = 'cascade')
    job_id = fields.Many2one('hr.job', string='Job Position', ondelete = 'cascade')
    department_id = fields.Many2one('hr.department', ondelete = 'cascade')
    schedule_id = fields.Many2one('hr.salary.schedule', string='Salary Schedule', ondelete = 'cascade')
    category_id = fields.Many2one('hr.contract.type', string='Contract Type', ondelete = 'cascade')
    company_id = fields.Many2one('res.company', ondelete = 'cascade')
    step_id = fields.Many2one('hr.salary.step', ondelete = 'cascade')

    contract = fields.Boolean(related = 'attribute_id.contract', readonly = True, string='Contract Level')
    contracts = fields.Boolean(related = 'attribute_id.contracts', readonly = True, string='Contracts Level')
    grade = fields.Boolean(related = 'attribute_id.grade', readonly = True, string='Grade Level')
    job = fields.Boolean(related = 'attribute_id.job', readonly = True, string='Job Level')
    department = fields.Boolean(related = 'attribute_id.department', readonly = True, string='Department Level')
    schedule = fields.Boolean(related = 'attribute_id.schedule', readonly = True, string='Schedule Level')
    category = fields.Boolean(related = 'attribute_id.category', readonly = True, string='Category Level')
    company = fields.Boolean(related = 'attribute_id.company', readonly = True, string='Company Level')    
    step = fields.Boolean(related = 'attribute_id.step', readonly = True, string='Step')
    
    description = fields.Char()
    approval_id = fields.Many2one('hr.attribute.value.approval', readonly = True)
    field_to_update_id = fields.Many2one('ir.model.fields', related='attribute_id.field_to_update_id')
    
    @api.constrains('attribute_id', 'approval_id', 'active', 'value', 'valid_from', 'valid_to')
    def _check_apprval(self):
        if self._uid ==1 or self._name != 'hr.attribute.value' or self._context.get('attribute_check_approval_skip'):
            return
        for record in self:
            if record.attribute_id.required_approval and not record.approval_id and record.contract_id.state !='draft':
                raise ValidationError(_('Approval Required'))
    
    @api.onchange('schedule_id')
    def _onchange_schedule_id(self):
        if self.grade_id and self.grade_id.schedule_id != self.schedule_id:
            self.grade_id = False
    
    @api.onchange('selection_id')
    def _onchange_attribute_id(self):
        if self.selection_id:
            self.value = self.selection_id[0].name
        else:
            self.value = False
    
    @api.constrains('selection_id') 
    def _compute_value(self):
        if self.selection_id:
            self.value = self.selection_id[0].name
        else:
            self.value = False
           
          
    @api.constrains('attribute_id', 'value')     
    def _check_value_type(self):
        for record in self:
            if record.attribute_id.type in ['int', 'float']:
                if record.attribute_id.value_type == 'positive' and float(record.value) < 0:
                    raise ValidationError("Value type is positive but the value is negative")
                if record.attribute_id.value_type == 'negative' and float(record.value) > 0:
                    raise ValidationError("Value type is negative but the value is positive")
    
    def name_get(self):
        res = []
        for record in self:
            valid_from = self.env['ir.qweb.field.date'].value_to_html(record.valid_from, {})            
            for fname in ['employee_id', 'grade_id', 'job_id','department_id','schedule_id','category_id','company_id']:
                name = record[fname].display_name
                if name:
                    break                
            if name:
                display = '%s - %s - %s' % (record.attribute_id.name, name, valid_from)
            else:
                display = '%s - %s' % (record.attribute_id.name, valid_from)
            res.append((record.id, display))
        return res
    
    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        for vals in vals_list:
            if self.env['hr.attribute'].browse(vals.get('attribute_id')).valid_to_required and not vals.get('valid_to'):
                vals['valid_to'] = vals.get('valid_from')
        return super(ContractAttribute, self).create(vals_list)
            
        
    def _search_isactive(self, operator, value):
        assert operator == '=' and value == True
        today = fields.Date.today()
        records = self.search([('active', operator, value), ('valid_from', '<=', today), '|', ('valid_to', '=', False), ('valid_to', '>=', today)])
        records = records.filtered('isactive')
        return [('id','in', records.ids)]
                    
    @api.onchange('employee_id')
    def _on_change_employee_id(self):
        if self.employee_id:
            self.contract_id = self.employee_id.contract_id
    
    @api.onchange('valid_from')
    def _onchange_valid_from(self):
        if self.valid_from and self.valid_to_required :
            if not self.valid_to or self.valid_to < self.valid_from:
                self.valid_to = self.valid_from
        
    @api.constrains('value', 'attribute_id')
    def _check_value(self):
        for record in self:
            try:
                value = record.attribute_id._get_value(record.value)
            except Exception as e:
                raise ValidationError(str(e))
            if record.attribute_id.has_selection:
                selections = record.attribute_id.get_selection()
                if value not in selections:
                    selections = record.attribute_id.get_selection(False)
                    raise ValidationError(_('Invalid Value, Available Values for %s are %s') % (record.attribute_id.name, ','.join(selections)))            
            
    
    @api.constrains('valid_from', 'valid_to')
    def _check_date(self):
        for record in self:
            if record.valid_to and record.valid_to < record.valid_from:
                raise ValidationError(_('Valid From >  Valid To'))

    @api.constrains('valid_to', 'attribute_id')
    def _check_valid_to(self):
        for record in self:
            if record.valid_to_required and not record.valid_to:
                raise ValidationError(_('Please Enter Valid To'))
    
    @api.depends('value', 'attribute_id', 'valid_from', 'valid_to')
    def _calc_isactive(self):
        today = fields.Date.today()
        for record in self:
            isactive = False
            domain = [('attribute_id','=', record.attribute_id.id), ('active', '=', True), ('valid_from', '<=', today), '|', ('valid_to', '=', False), ('valid_to', '>=', today)]
            for option in ['contract', 'contracts', 'job','grade', 'department','schedule','category','company']:
                if record.attribute_id[option]:
                    fname = '%s_id' % option
                    if option =='contracts':
                        args = [('contract_ids', 'in', record.contract_ids.ids)]
                    else:
                        args = [(fname, '=', record[fname].id)]
                    
                    isactive = record == self.search(args + domain, limit = 1)
                    break
            record.isactive = isactive
    
    def sync_field_value(self):
        for record in self:
            record.attribute_id._sync_field_values()
