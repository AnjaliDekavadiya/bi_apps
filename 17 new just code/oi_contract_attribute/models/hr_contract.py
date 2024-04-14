'''
Created on Oct 30, 2018

@author: Zuhair Hammadi
'''
from odoo import models, fields, api
from collections import OrderedDict
from odoo.tools.convert import safe_eval
from odoo.osv import expression
import datetime

class Contract(models.Model):
    _inherit= 'hr.contract'
    
    type_id = fields.Many2one(related='contract_type_id')

    attribute_value_ids = fields.One2many('hr.attribute.value', 'contract_id', string='Attributes', domain=['|',('active','=',False),('active','=',True)], copy = True)
    attribute_value_other_ids = fields.Many2many('hr.attribute.value', compute = '_calc_attribute_value_other_ids')
    
    attribute_count = fields.Integer(compute = '_calc_attribute_count')
    
    @api.depends('attribute_value_ids')
    def _calc_attribute_count(self):
        for record in self:
            record.attribute_count = len(record.attribute_value_ids.filtered('isactive'))
    
    @api.depends('employee_id', 'job_id', 'department_id', 'schedule_id', 'grade_id', 'type_id')
    def _calc_attribute_value_other_ids(self):
        for record in self:
            domains =  []
            if self.id:
                domains.append(['&', ('contract_ids','=', self.id), ('attribute_id.contracts','=', True)])
            if self.job_id:
                domains.append(['&', ('job_id','=', self.job_id.id), ('attribute_id.job','=', True)])
            if self.grade_id:
                domains.append(['&', ('grade_id','=', self.grade_id.id), ('attribute_id.grade','=', True)])
            if self.department_id:
                domains.append(['&', ('department_id','=', self.department_id.id), ('attribute_id.department','=', True)])
            if self.schedule_id:
                domains.append(['&', '&', ('schedule_id','=', self.schedule_id.id), ('attribute_id.schedule','=', True), ('grade_id','=', False)])
            if self.contract_type_id:
                domains.append(['&', ('category_id','=', self.contract_type_id.id), ('attribute_id.category','=', True)])
            if self.employee_id.company_id:
                domains.append(['&', ('company_id','=', self.employee_id.company_id.id), ('attribute_id.company','=', True)])
            domain = [('active','=', True), ('attribute_id.active','=', True)] + expression.OR(domains)
            record.attribute_value_other_ids = self.env['hr.attribute.value'].search(domain)
                    
    def _getAttribute(self, code, date = None, date_from = None, date_to = None):
        attribute_id = self.env['hr.attribute'].search([('code','=', code), ('active','=', True)], limit = 1)
        attribute_value_id = self.env['hr.attribute.value']
        if not self:
            return attribute_id, attribute_value_id
        
        today = date or self._context.get('date') or fields.Date.today()        
        date_from = date_from or self._context.get('date_from') or today
        date_to = date_to or self._context.get('date_to') or today
        
        if attribute_id:            
            domain = [('attribute_id','=', attribute_id.id), 
                      ('active','=', True),
                      ('valid_from', '<=', date_to),
                      '|', ('valid_to','=', False), ('valid_to', '>=', date_from)]
                                    
            for option, args in [('contract', [('contract_id','=', self.id or 0)]),   
                                 ('contracts', [('contract_ids','=', self.id or 0)]),                               
                                  ('job', [('job_id','=', self.job_id.id or 0)]),
                                  ('step', [('step_id','=', self.step_id.id or 0)]),
                                  ('grade', [('grade_id','=', self.grade_id.id or 0)]),
                                  ('department', [('department_id','=', self.department_id.id or 0)]),
                                  ('schedule', [('schedule_id','=', self.schedule_id.id or 0), ('grade_id','=', False)]),
                                  ('category', [('category_id','=', self.type_id.id or 0)]),
                                  ('company', [('company_id','=', self.employee_id.company_id.id or 0)]),
                                  ]:
                if attribute_id[option]:
                    attribute_value_id = self.env['hr.attribute.value'].search(args + domain, limit = 1)
                    if attribute_value_id:
                        break
                                   
        return attribute_id,attribute_value_id
    
    def getAttribute(self, code, date = None, date_from = None, date_to = None):
        attribute_id, contract_attribute_id = self._getAttribute(code, date=date, date_from=date_from, date_to=date_to)
        return attribute_id._get_value(contract_attribute_id.value)
    
    def getAttributeInfo(self, code, date = None, date_from = None, date_to = None):
        _, contract_attribute_id = self._getAttribute(code, date=date, date_from=date_from, date_to=date_to)
        return contract_attribute_id.description
        
    def getAttributeSum(self, code, date_from, date_to):
        attribute_id = self.env['hr.attribute'].search([('code','=', code)], limit = 1)
        assert attribute_id.type in ['int', 'float']            
        assert attribute_id.contract            
        res = []
        func = safe_eval(attribute_id.type)
        for record in self.env['hr.attribute.value'].search([('contract_id','=', self.id), 
                                                                  ('attribute_id','=', attribute_id.id), 
                                                                  ('active','=', True),
                                                                  ('valid_from', '<=', date_to),
                                                                  ('valid_to','>=', date_from)]):
            res.append(record.value)
        res = map(func, res)
        return sum(res)
        
    def attribute_report(self):
        attribute_ids = self.env['hr.attribute'].search([])
        rows = []
        for record in self:
            vals = OrderedDict()
            vals['Reference']=record.name 
            vals['Employee']=record.employee_id.name            
            for attribute_id in attribute_ids:
                vals[attribute_id.name] = record.getAttribute(attribute_id.code)
            rows.append(vals)
        return self.env['oi_excel_export'].export(rows, header_columns_count=2) 
    
    def action_attribute(self):
        action, = self.env.ref('oi_contract_attribute.act_hr_attribute_value').read()
        action['domain'] = [('contract_id','=', self.id)]
        context = safe_eval(action.get('context') or '{}')
        context['default_contract_id'] = self.id
        action['context'] = context
        action['views'] = [(self.env.ref('oi_contract_attribute.view_hr_attribute_value_tree_emp').id, 'tree'), (self.env.ref('oi_contract_attribute.view_hr_attribute_value_form_emp').id, 'form')]
        return action
    
    def getAttributeByDay(self, code, date_from = None, date_to = None, max_days = 30):
        date_from = date_from or self._context.get('date_from')
        date_to = date_to or self._context.get('date_to')
        domain = [
          ('contract_id','=', self.id),
          ('attribute_id.code','=', code),
          ('active','=', True),
          ('valid_from', '<=', date_to),
          '|', ('valid_to','=', False), ('valid_to', '>=', date_from)
          ]
        assert date_to >= date_from, 'Date From > Date To'
        
        attribute_value_ids = self.env['hr.attribute.value'].search(domain)
        if not attribute_value_ids:
            return 0
        
        dt = date_from
        total_days = 0
        alw_value = 0

        while dt <= date_to:
            total_days += 1
            for attribute_value_id in attribute_value_ids:
                if attribute_value_id.valid_from <= dt and (not attribute_value_id.valid_to or attribute_value_id.valid_to >=dt):
                    alw_value += float(attribute_value_id.value)
                    break
              
            dt += datetime.timedelta(days=1)
            if max_days and total_days >= max_days:
                break
                                  
        return total_days and alw_value / total_days

    def write(self, vals):
        res = super(Contract, self).write(vals)
        if not self._context.get("from_attr_sync"):
            employee_ids = self.mapped('employee_id').ids
            if employee_ids:
                for employee_id in employee_ids:
                    self.env['hr.attribute'].sudo().with_context(employee_id = employee_id)._sync_field_values()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        contracts = super().create(vals_list)
        for contract in contracts:
            self.env['hr.attribute'].sudo().with_context(employee_id = contract.employee_id.id)._sync_field_values()
        return contracts