# -*- coding:utf-8 -*-

import base64
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TaskReview(models.TransientModel):
    _name = 'task.review.customer.custom'
    _description = 'Task Review Customer'

    rating = fields.Text(
        string="Review for",
        required=True,
    )
    project_id = fields.Many2one(
        'project.project',
        string="Project",
        readonly=True,
    )
    task = fields.Char(
        string="Task",
        readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string="Customer",
        readonly=True,
    )
    datas_fname = fields.Char('Import File Name')
    
    #@api.multi
    def project_rating(self):
        active_id = self._context.get('active_id')
        task_obj = self.env['project.task'].browse(active_id)
        task_obj.request_rating_custom = self.rating
        if task_obj.project_id:
            template = self.env.ref('project_task_issue_rating.email_template_task_review_custom')
            template.send_mail(task_obj.id, force_send=True)
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
        
