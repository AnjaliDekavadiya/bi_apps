# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. 
# See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from odoo import models, fields, api
import datetime
import calendar
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ProjectTask(models.Model):
    _inherit = 'project.task'


    is_task_template = fields.Boolean(
        string="Is Task Template",
        copy=False
    )
    is_task_checklist = fields.Boolean(
        string="Is Checklist Task",
        copy=False
    )
    checklist_task_id = fields.Many2one(
        'project.task',
        string='Checklist Parent Task'
    )
    task_line_checklist_ids = fields.One2many(
        'project.task',
        'checklist_task_id',
        string="Task Checklist",
    )
    is_checklist_template = fields.Boolean(
        string="Is Checklist Template",
        copy=False
    )

    # @api.model
    # def search(self, args, offset=0, limit=None, order=None, count=False):
    #     if self._context.get('search_default_my_tasks'):
    #         args += [('is_checklist_template', '=', False),
    #                  ('is_task_checklist','=',False),
    #                  ('is_task_template','=',False)
    #                 ]
    #     res = super(ProjectTask, self).search(args, offset, limit, order, count)
    #     return res

    @api.model
    def search(self, args, offset=0, limit=None, order=None):
        if self._context.get('search_default_my_tasks'):
            args += [('is_checklist_template', '=', False),
                     ('is_task_checklist','=',False),
                     ('is_task_template','=',False)
                    ]
        res = super(ProjectTask, self).search(args, offset, limit, order)
        return res

    @api.model
    def _cron_create_recurring_task(self):
        today = fields.date.today()
        user_lang =  self.env.user.lang
        lang = self.env['res.lang'].search([('code','=',user_lang)],limit=1)
        if lang:
            date_format = lang.date_format
            format_change = today.strftime(date_format)
        else:
            today.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        monthly_date = today.replace(day=1)
        date = today.strftime('%B -%Y')
        if today == monthly_date:
            monthly_task_recurring_ids = self.env['recurring.task'].search([('task_recurring', '=', 'monthly')])
            for monthly_rec_task_id in monthly_task_recurring_ids.mapped("task_id"):
                monthly_list = []
                for monthly_checklist_id in monthly_rec_task_id.task_line_checklist_ids:
                    monthly_list.append(
                        (0, 0, {'name': monthly_checklist_id.name}
                                )
                    )
                new_task_id = monthly_rec_task_id.copy(default={'name': monthly_rec_task_id.name +'('+ str(date) + ')',
                        'task_line_checklist_ids':monthly_list})
                new_task_id.task_line_checklist_ids.write({
                    'is_task_checklist':True,
                    'project_id':monthly_rec_task_id.project_id.id,
                    # 'user_id':monthly_rec_task_id.user_id.id,
                    'user_ids':monthly_rec_task_id.user_ids.ids,
                    'stage_id':monthly_rec_task_id.stage_id.id
                })

        week_day_date = today - timedelta(days=today.weekday())
        end_of_week = week_day_date + timedelta(days=6)
        if today == week_day_date:
            weekly_task_recurring_ids = self.env['recurring.task'].search([('task_recurring', '=', 'weekly')])
            for weekly_rec_task_id in weekly_task_recurring_ids.mapped("task_id"):
                checklist = []
                for weekly_line_checklist_id in weekly_rec_task_id.task_line_checklist_ids:
                    checklist.append(
                        (0, 0, {'name': weekly_line_checklist_id.name}
                                )
                    )
                new_task_id = weekly_rec_task_id.copy(default={'name': weekly_rec_task_id.name+'(' + week_day_date.strftime(date_format) +'to'+ end_of_week.strftime(date_format) + ')',
                        'task_line_checklist_ids':checklist })
                new_task_id.task_line_checklist_ids.write({
                    'is_task_checklist':True,
                    'project_id':weekly_rec_task_id.project_id.id,
                    # 'user_id':weekly_rec_task_id.user_id.id,
                    'user_ids':weekly_rec_task_id.user_ids.ids,
                    'stage_id':weekly_rec_task_id.stage_id.id
                })

        yearly_date = today.replace(month=1)
        year_date = yearly_date.replace(day=1)
        if today ==  year_date:
            yearly_task_recurring_ids = self.env['recurring.task'].search([('task_recurring', '=', 'yearly')])
            for yearly_rec_task_id in yearly_task_recurring_ids.mapped("task_id"):
                yearly_checklist = []
                for yearly_checklist_id in yearly_rec_task_id.task_line_checklist_ids:
                    yearly_checklist.append(
                        (0, 0, {'name': yearly_checklist_id.name}
                                )
                    )
                new_task_id = yearly_rec_task_id.copy(default={'name': yearly_rec_task_id.name +'(' + year_date.strftime(date_format) + ')',
                        'task_line_checklist_ids':yearly_checklist })
                new_task_id.task_line_checklist_ids.write({
                    'is_task_checklist':True,
                    'project_id':yearly_rec_task_id.project_id.id,
                    # 'user_id':yearly_rec_task_id.user_id.id,
                    'user_ids':yearly_rec_task_id.user_ids.ids,
                    'stage_id':yearly_rec_task_id.stage_id.id
                })

        daily_task_recurring_ids = self.env['recurring.task'].search([('task_recurring', '=', 'daily')])
        for daily_rec_task_id in daily_task_recurring_ids.mapped("task_id"):
            checklist_line_lst = []
            for task_line_checklist_id in daily_rec_task_id.task_line_checklist_ids:
                checklist_line_lst.append(
                    (0, 0, {'name': task_line_checklist_id.name}
                            )
                )
            new_task_id = daily_rec_task_id.copy(default={'name': daily_rec_task_id.name + '(' + format_change + ')',
                                'task_line_checklist_ids': checklist_line_lst,'stage_id':daily_rec_task_id.stage_id.id})
            new_task_id.task_line_checklist_ids.write({
                    'is_task_checklist':True,
                    'project_id':daily_rec_task_id.project_id.id,
                    # 'user_id':daily_rec_task_id.user_id.id,
                    'user_ids':daily_rec_task_id.user_ids.ids,
                    'stage_id':daily_rec_task_id.stage_id.id
                })

    # @api.multi #odoo13
    def action_view_checklist(self):
        self.ensure_one()
        action = self.env.ref('project_recurring_task_checklist.action_view_task_checklists').sudo().read()[0]
        action['domain'] = str([('checklist_task_id', 'in', self.ids)])
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: