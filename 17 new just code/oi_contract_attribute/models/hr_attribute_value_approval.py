'''
Created on May 5, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_states = {'draft' : [('readonly', False)]}

class ContractAttributeApproval(models.Model):
    _name= 'hr.attribute.value.approval'
    _description = 'Employee Attribute Approval'
    
    _inherit = ['hr.attribute.value', 'approval.record', 'mail.thread', 'mail.activity.mixin']
    
    attribute_id = fields.Many2one(readonly = True,  )    
    valid_from = fields.Date(readonly = True,  )
    valid_to = fields.Date(readonly = True,  )
    value = fields.Char(readonly = True,  )
    
    contract_id = fields.Many2one(readonly = True,  )
    contract_ids = fields.Many2many(readonly = True,  )
    employee_id = fields.Many2one(readonly = True,  )
    
    grade_id = fields.Many2one(readonly = True,  )
    job_id = fields.Many2one(readonly = True,  )
    department_id = fields.Many2one(readonly = True,  )
    schedule_id = fields.Many2one(readonly = True,  )
    category_id = fields.Many2one(readonly = True,  )
    company_id = fields.Many2one(readonly = True,  )
        
    update_type = fields.Selection([('new', 'New'), ('update', 'Update'), ('remove', 'Remove')], required = True, default = 'new', readonly = True,  ) 
    update_attribute_value_id = fields.Many2one('hr.attribute.value', string='Attribute value', readonly = True,  )
                
    def _on_approve(self):
        super(ContractAttributeApproval, self)._on_approve()
        vals= {}
        for name,field in self.env['hr.attribute.value']._fields.items():
            if field.store and not field.automatic and name in self:
                vals[name] = self[name]
        vals['approval_id'] = self
        vals = self.env['hr.attribute.value']._convert_to_write(vals)
        if self.update_type=='new':
            self.env['hr.attribute.value'].sudo().create(vals)
        elif self.update_type=='update':
            self.update_attribute_value_id.sudo().write(vals)
        elif self.update_type=='remove':
            self.update_attribute_value_id.sudo().write({'active' : False})                             
    
    @api.onchange('update_attribute_value_id')
    def _onchange_update_attribute_value_id(self):
        if self.update_attribute_value_id:
            vals= {}
            for name,field in self.env['hr.attribute.value']._fields.items():
                if field.store and not field.automatic and name in self:
                    vals[name] = self.update_attribute_value_id[name]
            self.update(vals)
            
    def unlink(self):
        if any(self.filtered(lambda record : record.state!='draft')):
            raise UserError(_('You can delete draft status only'))
        return super(ContractAttributeApproval, self).unlink()                