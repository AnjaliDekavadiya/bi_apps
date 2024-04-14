# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. 
# See LICENSE file for full copyright and licensing details.


from odoo import models, fields, api
from lxml import etree
import ast
from odoo.addons.project.models.project_task import PROJECT_TASK_READABLE_FIELDS

# from odoo.addons.project.models.project_task import PROJECT_TASK_READABLE_FIELDS

PROJECT_TASK_READABLE_FIELDS.update({
    'custom_is_task_template'
})

class ProjectTask(models.Model):
    _inherit = 'project.task'


    custom_is_task_template = fields.Boolean(
        string="Is Task Template?",
        copy=True
    )


    @api.model
    # def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        if self._context.get('custom_special_task_template'):
            domain += [('custom_is_task_template', '=', True),
                    ]
        elif self._context.get('custom_special_project_template'):
            domain += [('custom_is_task_template', '=', True),
                    ]
        elif self._context.get('default_project_id'):
            custom_pro_id = self.env['project.project'].browse(self._context.get('default_project_id'))
            if custom_pro_id.custom_is_project_template:
                domain += [('custom_is_task_template', '=', True),
                    ]
        else:
            domain += [('custom_is_task_template', '=', False),
                    ]
        res = super(ProjectTask, self)._search(domain, offset, limit, order, access_rights_uid)
        return res

    def custom_create_task(self):
        for rec in self:
            new_task_id = rec.copy(default={'custom_is_task_template':False,
                        })
            subtasks = self.env['project.task']
            for child_task in rec.child_ids:
                subtask_vals = {'custom_is_task_template': False, 'parent_id': new_task_id.id}
                subtasks += child_task.copy(default=subtask_vals)
                print('--------subtask-----',subtasks)
            new_task_id.write({'child_ids': [(6, 0, subtasks.ids)]})
        action = self.env.ref('project.action_view_task')
        result = action.sudo().read()[0]
        context = ast.literal_eval(action['context'])
        context.update({'custom_special_task_template': False})
        result['context'] = context
        result['domain'] = [('id', '=', new_task_id.id)]
        return result

    def custom_create_task_template(self):
        for rec in self:
            new_task_id = rec.copy(default={'custom_is_task_template':True})
        action = self.env.ref('odoo_task_project_template.action_view_task_template_custom')
        result = action.sudo().read()[0]
        result['domain'] = [('id', '=', new_task_id.id)]
        return result

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ProjectTask, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if self._context.get('custom_special_task_template'):
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='project_id']"):
                node.set('context', "{'custom_special_project_template': True}")
            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res

    # @api.model_create_multi
    # def create(self, vals_list):
    #     tasks = super(ProjectTask, self).create(vals_list)
    #     for task in tasks:
    #         if task.project_id.custom_is_project_template\
    #         and not task.custom_is_task_template:
    #             task.custom_is_task_template = True
    #     return tasks


    @api.model
    def default_get(self, fields):
        res = super(ProjectTask, self).default_get(fields)
        if self._context.get('custom_special_task_template'): 
            res['custom_is_task_template'] = True
        return res
