# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ProjectTask(models.Model):
    _inherit = 'project.task'
    
    #@api.one
    def action_task_rating_custom(self):
        self.ensure_one()
        if self.project_id:
            template = self.env.ref('project_task_issue_rating.email_template_task_requested')
            template.send_mail(self.id, force_send=True)
    
    customer_review_comment = fields.Text(
        string='Comment',
        readonly=True,
        copy=False,
    )
    customer_custom_rating = fields.Selection(
        [('poor', 'Poor'),
        ('average', 'Average'),
        ('good', 'Good'),
        ('very good', 'Very Good'),
        ('excellent', 'Excellent')],
        string='Customer Review',
        readonly=True,
        copy=False,
    )
    request_rating_custom = fields.Text(
        string='Request Review',
        copy=False,
    )

    def get_mail_access_url(self):
        return '/manager_review_request/review/'+str(self.id)

    
# class ProjectIssue(models.Model):
#     _inherit = 'project.issue'
#     
#     @api.one
#     def action_issue_rating(self):
#         if self.partner_id:
#             template = self.env.ref('project_task_issue_rating.email_template_issue_requested')
#             template.send_mail(self.id, force_send=True)
#         if self.email_from:
#             template = self.env.ref('project_task_issue_rating.email_template_issue_no_customer_request')
#             template.send_mail(self.id, force_send=True)
#     
#     comment = fields.Text(
#         string='Comment',
#         readonly=True,
#         copy=False,
#     )
#     rating = fields.Selection(
#         [('poor', 'Poor'),
#         ('average', 'Average'),
#         ('good', 'Good'),
#         ('very good', 'Very Good'),
#         ('excellent', 'Excellent')],
#         string='Feedback',
#         readonly=True,
#         copy=False,
#     )
#     request_issue = fields.Text(
#         string='Request Feedback',
#     )
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
