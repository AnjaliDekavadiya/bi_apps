# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ProjectTask(models.Model):
    _inherit = "project.task"

    # @api.multi
    # @api.depends('name', 'number')
    # def name_get(self):
    #     result = []
    #     for task in self:
    #         if task.number:
    #             name = task.name + ' ' + task.number
    #             # result.append((task.id, name))
    #         else:
    #             name = task.name
    #         result.append((task.id, name))
    #     return result

    @api.depends('name', 'number')
    def _compute_display_name(self):
        for task in self:
            if task.name:
                task.display_name = task.name + ' ' + task.number
                # result.append((task.id, name))
            else:
                task.display_name = task.name
        
    # @api.model
    # def create(self,vals):
    #     project_obj = self.env['project.project']
    #     project_id = vals.get('project_id')
    #     custom_ctx = self._context.copy()
    #     if not project_id:
    #         if custom_ctx.get('default_project_id', False):
    #             project_id = custom_ctx['default_project_id']
    #     project =  project_obj.browse(project_id)
    #     if project:
    #         if vals.get('project_id', False) != False or custom_ctx.get('default_project_id', False):
    #             next_number = project.entry_sequence.code
    #             if next_number:
    #                 number = self.env['ir.sequence'].next_by_code(next_number)
    #                 vals.update({
    #                     # 'number': project.number+'-'+number,
    #                     'number': project.number and number and project.number+'-'+number or project.number and not number and project.number or number and not project.number and number or ''
    #                     })
    #             else:
    #                 number = self.env['ir.sequence'].next_by_code('project.task')
    #                 vals.update({
    #                 'number': number,
    #                 })
    #     else:
    #         number = self.env['ir.sequence'].next_by_code('project.task')
    #         vals.update({
    #             'number': number,
    #             })

    #     result = super(ProjectTask, self).create(vals)
    #     return result

    @api.model_create_multi
    def create(self,vals_list):
        for vals in vals_list:
            project_obj = self.env['project.project']
            project_id = vals.get('project_id')
            custom_ctx = self._context.copy()
            if not project_id:
                if custom_ctx.get('default_project_id', False):
                    project_id = custom_ctx['default_project_id']
            project =  project_obj.browse(project_id)
            if project:
                if vals.get('project_id', False) != False or custom_ctx.get('default_project_id', False):
                    next_number = project.entry_sequence.code
                    if next_number:
                        number = self.env['ir.sequence'].next_by_code(next_number)
                        vals.update({
                            # 'number': project.number+'-'+number,
                            'number': project.number and number and project.number+'-'+number or project.number and not number and project.number or number and not project.number and number or ''
                            })
                    else:
                        number = self.env['ir.sequence'].next_by_code('project.task')
                        vals.update({
                        'number': number,
                        })
            else:
                number = self.env['ir.sequence'].next_by_code('project.task')
                vals.update({
                    'number': number,
                    })
        result = super(ProjectTask, self).create(vals_list)
        return result
        
    # @api.multi
    def write(self, vals):
        project_obj = self.env['project.project']
        project_id = vals.get('project_id')
        project =  project_obj.browse(project_id)
        if 'project_id' in vals:
            if vals['project_id'] != False:
                next_number = project.entry_sequence.code
                if next_number:
                    number = self.env['ir.sequence'].next_by_code(next_number)
                    vals.update({
                        # 'number': project.number+'-'+number,
                        'number': project.number and number and project.number+'-'+number or project.number and not number and project.number or number and not project.number and number or ''
                        })
                else:
                    number = self.env['ir.sequence'].next_by_code('project.task')
                    vals.update({
                    'number': number,
                    })
            elif  self.project_id:
                number = self.env['ir.sequence'].next_by_code('project.task')
                vals.update({
                    'number': number,
                    })
                
        result = super(ProjectTask, self).write(vals)
        return result
        
    number = fields.Char(
        string='Number',
        readonly= True,
        required=False,
        copy=False,
        default=lambda self: _('New'),
    )
