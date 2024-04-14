# # -*- coding: utf-8 -*-
# 
# from odoo import models, fields, api, _
# 
# class ProjectIssue(models.Model):
#     _inherit = "project.issue"
# 
#     @api.multi
#     @api.depends('name', 'number')
#     def name_get(self):
#         result = []
#         for issue in self:
#             name = issue.name + ' ' + issue.number
#             result.append((issue.id, name))
#         return result
#     
#     @api.model
#     def create(self,vals):
#         project_obj = self.env['project.project']
#         project_id = vals.get('project_id')
#         project =  project_obj.browse(project_id)
#         if project:
#             if vals['project_id'] != False:
#                 next_number = project.entry_issue_sequence.code
#                 if next_number:
#                     number = self.env['ir.sequence'].next_by_code(next_number)
#                     vals.update({
#                         'number': project.number+'-'+number,
#                         })
#                 else:
#                     number = self.env['ir.sequence'].next_by_code('project.issue')
#                     vals.update({
#                     'number': number,
#                     })
#         else:
#             number = self.env['ir.sequence'].next_by_code('project.issue')
#             vals.update({
#                 'number': number,
#                 })
#                 
#         result = super(ProjectIssue, self).create(vals)
#         return result
#         
#     @api.multi
#     def write(self, vals):
#         project_obj = self.env['project.project']
#         project_id = vals.get('project_id')
#         project =  project_obj.browse(project_id)
#         if 'project_id' in vals:
#             if vals['project_id'] != False:
#                 next_number = project.entry_issue_sequence.code
#                 if next_number:
#                     number = self.env['ir.sequence'].next_by_code(next_number)
#                     vals.update({
#                         'number': project.number+'-'+number,
#                         })
#                 else:
#                     number = self.env['ir.sequence'].next_by_code('project.issue')
#                     vals.update({
#                     'number': number,
#                     })
#             elif self.project_id:
#                 number = self.env['ir.sequence'].next_by_code('project.task')
#                 vals.update({
#                     'number': number,
#                     })
#                     
#         result = super(ProjectIssue, self).write(vals)
#         return result
#         
#     number = fields.Char(
#         string='Number',
#         readonly= True,
#         required=False,
#         copy=False,
#         default=lambda self: _('New'),
#     )
