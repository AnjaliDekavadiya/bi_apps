# -*- coding: utf-8 -*-

from odoo import fields, models, api
import ast


class Project(models.Model):
    _inherit = "project.project"

    custom_is_project_template = fields.Boolean(
        string="Is Project Template?",
        copy=True
    )

    def _compute_task_count(self):
        res= super(Project, self)._compute_task_count()
        if self._context.get('custom_special_project_template'):
            task_data = self.env['project.task'].read_group([('project_id', 'in', self.ids), '|', ('stage_id.fold', '=', False), ('stage_id', '=', False),('custom_is_task_template','=',True)], ['project_id'], ['project_id'])
        else :
            task_data = self.env['project.task'].read_group([('project_id', 'in', self.ids), '|', ('stage_id.fold', '=', False), ('stage_id', '=', False),('custom_is_task_template','=',False)], ['project_id'], ['project_id'])                    
        result = dict((data['project_id'][0], data['project_id_count']) for data in task_data)
        for project in self:
            project.task_count = result.get(project.id, 0)
            # project.task_count_with_subtasks = result.get(project.id, 0)
            project.closed_task_count = result.get(project.id, 0)
        return res

    # @api.model
    # # def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
    # def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
    #     if self._context.get('special'):
    #         return super(Project, self)._search(domain, offset, limit, order, access_rights_uid)
    #     if not self._context.get('custom_special_project_template'):
    #         domain += [('custom_is_project_template', '=', False),
    #                 ] 
    #     else:
    #         domain += [('custom_is_project_template', '=', True),
    #                 ]
    #     res = super(Project, self)._search(domain, offset, limit, order, access_rights_uid)
    #     return res
    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        if self._context.get('special'):
            return super(Project, self)._search(domain, offset, limit, order, access_rights_uid)
        if self._context.get('custom_special_project_template'):
            domain += [('custom_is_project_template', '=', True),
                    ]
        # res = super(Project, self)._search(domain, offset, limit, order, access_rights_uid)
        return super(Project, self)._search(domain, offset, limit, order, access_rights_uid)

    def custom_create_project(self):
        for rec in self:
            new_project_id = rec.copy(default={'custom_is_project_template':False,
                        })
            for new_task in new_project_id.task_ids:
                new_task.custom_is_task_template = False
        action = self.env.ref('project.open_view_project_all')
        result = action.sudo().read()[0]
        context = ast.literal_eval(action['context'])
        context.update({'custom_special_project_template': False})
        result['context'] = context
        result['domain'] = [('id', '=', new_project_id.id)]
        return result

    def custom_create_project_template(self):
        for rec in self:
            new_project_id = rec.copy(default={'custom_is_project_template':True,
                        })
            for new_task in new_project_id.task_ids:
                new_task.custom_is_task_template = True
        action = self.env.ref('odoo_task_project_template.open_view_project_template_custom_all')
        result = action.sudo().read()[0]
        result['domain'] = [('id', '=', new_project_id.id)]
        return result