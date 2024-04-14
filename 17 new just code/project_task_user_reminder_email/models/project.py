# -*- coding: utf-8 -*-

from datetime import date
from datetime import datetime

from odoo import api, fields, models, _

class ProjectTask(models.Model):

    _inherit = "project.task"

    task_reminder = fields.Boolean(
        "Task Reminder",
        default=True,
        help="Tick this box if you want to get reminder alert by email when task reach deadline."
    )

    # @api.model
    # def _cron_project_task_reminder(self):
    #     action_id = self.env.ref('project.action_view_task')
    #     port = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    #     data_base = self._cr.dbname
    #     obj = 'project.task'
    #     reminder_mail_template = self.env.ref('project_task_user_reminder_email.task_reminder_mail_template')
        
    #     today_date = datetime.now().strftime('%Y-%m-%d')
    #     self._cr.execute("""
    #         SELECT id ,user_id, name, date_deadline, project_id, sequence
    #         from project_task
    #         where 
    #             to_char(date_deadline, 'YYYY-MM-DD') = '%s' AND
    #             task_reminder = True
    #         group by user_id,id
    #     """%(today_date)
    #     )
    #     task_ids = self._cr.dictfetchall()
    #     date =  datetime.strftime(datetime.strptime(today_date, '%Y-%m-%d'), '%d-%m-%Y')
    #     ctx = self._context.copy()
    #     ctx.update({'today_date':date, 'action_id':action_id.id, 'port':port, 'data_base_name':data_base, 'obj':obj})
    #     user_tasks = {}
    #     for task in task_ids:
    #         project_id = task['project_id']
    #         project = self.env['project.project'].browse(project_id)
    #         task['project_id'] = project.name
    #         user_id = task['user_id']
    #         user = self.env['res.users'].browse(user_id)
    #         task.update({'manager_name':project.user_id.name})
    #         if task['user_id'] not in user_tasks:
    #             user_tasks[task['user_id']] = [task]
    #         else:
    #             user_tasks[task['user_id']].append(task)
    #     for user in user_tasks:
    #         ctx.update({'task_data': user_tasks[user]})
    #         reminder_mail_template.with_context(ctx).send_mail(user)
    #     return True
    

    @api.model
    def _cron_project_task_reminder(self):
        action_id = self.env.ref('project.action_view_task')
        port = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        data_base = self._cr.dbname
        obj = 'project.task'
        reminder_mail_template = self.env.ref('project_task_user_reminder_email.task_reminder_mail_template')
        
        today_date = datetime.now().strftime('%Y-%m-%d')
        task_ids = self.env['project.task'].search([('date_deadline','=',today_date),('task_reminder','=',True)])
        date =  datetime.strftime(datetime.strptime(today_date, '%Y-%m-%d'), '%d-%m-%Y')
        ctx = self._context.copy()
        ctx.update({'today_date':date, 'action_id':action_id.id, 'port':port, 'data_base_name':data_base, 'obj':obj})
        user_tasks = {}
        
        for task in task_ids:
            project_id = task['project_id']
            task['project_id'] = project_id
            for u in task.user_ids:
                if u.id not in user_tasks:
                    user_tasks[u.id] = [task]
                else:
                    user_tasks[u.id].append(task)

            for user in user_tasks:
                ctx.update({'task_data': user_tasks[user]})
                reminder_mail_template.with_context(ctx).send_mail(user)
        return True
