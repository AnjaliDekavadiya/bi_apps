# -*- coding: utf-8 -*-
import uuid

from odoo import models, fields, api, _

class Project(models.Model):
    _inherit = "project.project"
    
#     @api.model
#     def create(self,vals):
#         code = uuid.uuid4()
#         code_issue = uuid.uuid4()
        
#         number = self.env['ir.sequence'].next_by_code('project.project')
#         if vals.get('prefix', False):
#             pre_val = vals['prefix']
#         else:
#             pre_val = False
#         if pre_val:
#             number_list = number.split('/')
#             pre_number = number_list[-1:][0]
#             number = pre_val + '/' + pre_number
            
#         task_vals = {
#                 'code' : code,
#                 'name': 'Task' + ' ' + vals['name'],
#                 'padding' : 4,
#             }
#         task_seq_obj = self.env['ir.sequence'].sudo().create(task_vals)
        
# #         issue_vals = {
# #                 'code' : code_issue,
# #                 'name': 'Issue' + ' ' + vals['name'],
# #                 'padding' : 4,
# #             }
# #         issue_seq_obj=self.env['ir.sequence'].sudo().create(issue_vals)
        
#         vals.update({
#             'number': number,
#             'entry_sequence':task_seq_obj.id,
# #             'entry_issue_sequence':issue_seq_obj.id,
#             })
#         result = super(Project, self).create(vals)
#         return result 

    @api.model_create_multi
    def create(self,vals_list):
        code = uuid.uuid4()
        code_issue = uuid.uuid4()
        
        number = self.env['ir.sequence'].next_by_code('project.project')
        for vals in vals_list:
            if vals.get('prefix', False):
                pre_val = vals['prefix']
            else:
                pre_val = False
            if pre_val:
                number_list = number.split('/')
                pre_number = number_list[-1:][0]
                number = pre_val + '/' + pre_number
                
            task_vals = {
                    'code' : code,
                    'name': 'Task' + ' ' + vals['name'],
                    'padding' : 4,
                }
            task_seq_obj = self.env['ir.sequence'].sudo().create(task_vals)
            
    #         issue_vals = {
    #                 'code' : code_issue,
    #                 'name': 'Issue' + ' ' + vals['name'],
    #                 'padding' : 4,
    #             }
    #         issue_seq_obj=self.env['ir.sequence'].sudo().create(issue_vals)
            
            vals.update({
                'number': number,
                'entry_sequence':task_seq_obj.id,
    #             'entry_issue_sequence':issue_seq_obj.id,
                })
        result = super(Project, self).create(vals_list)
        return result 
        
    number = fields.Char(
        string='Number',
        readonly= True,
        required=True,
        copy=False,
        default=lambda self: _('New'),
    )
    prefix = fields.Char(
        'Prefix',
    )
    entry_sequence = fields.Many2one(
        'ir.sequence',
        string='Task Entry Sequence',
        copy=False,
    )
    entry_issue_sequence = fields.Many2one(
        'ir.sequence',
        string='Issue Entry Sequence',
        copy=False,
    )
    
    
    # @api.multi
    def write(self,vals):
        pre_val = vals.get('prefix')
        # number = self.number
        if vals.get('number'):
            number = vals.get('number')
        if pre_val:
            if not vals.get('number'):
                number = self.number
            number_list = number.split('/')
            pre_number = number_list[-1:][0]
            number = pre_val + '/' + pre_number
            vals.update({
                'number':number,
            })
        return super(Project, self).write(vals) 
