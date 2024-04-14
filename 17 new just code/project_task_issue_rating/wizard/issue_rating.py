# -*- coding:utf-8 -*-

from odoo import models, fields, api, _

class IssueFeedbackWizard(models.TransientModel):
    _name = 'issue.feedback.wizard'
    _description = 'Issue Feedback Wizard'

    feedback = fields.Text(
        string="Feedback for",
        required=True,
    )
    project_id = fields.Many2one(
        'project.project',
        string="Project",
        readonly=True,
    )
    issue = fields.Char(
        string="Issue",
        readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string="Customer",
        readonly=True,
    )
    
    #@api.multi
    def issue_rating(self):
        active_id = self._context.get('active_id')
        issue_obj = self.env['project.issue'].browse(active_id)
        issue_obj.request_issue = self.feedback
        if issue_obj.partner_id:
            template = self.env.ref('project_task_issue_rating.email_template_issue_requested')
            template.send_mail(issue_obj.id, force_send=True)
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
