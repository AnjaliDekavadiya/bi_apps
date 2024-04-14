# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
#from odoo.addons.website_portal.controllers.main import website_account

class TaskIssueRequest(http.Controller):
    
    @http.route(['/manager_review_request/review/<int:task_id>'], type='http', auth='user', website=True)
    def feedback_email_custom(self, task_id, **kw):
        task_obj = request.env['project.task'].sudo().browse(task_id)
        values = {
            'message' : task_obj.request_rating_custom,
            'project':  task_obj.project_id.name,
            'task':  task_obj.name,
            'customer' : task_obj.partner_id.name,
            }
        values.update({'task_id': task_id})
        return request.render("project_task_issue_rating.task_feedback_custom_review", values) 

    @http.route(['/project_task/review/'],
                type='http', auth='user', website=True)
    def start_rating(self, **kw):
        partner_id = kw['partner_id']
        task_obj = request.env['project.task'].sudo().browse(int(kw['task_id']))
        vals = {
              'customer_custom_rating':kw['star'],
              'customer_review_comment':kw['comment'],
            }
        task_obj.sudo().write(vals)
        customer_msg = _(task_obj.project_id.partner_id.name +" "+' has sent review rating is %s and comment is: %s') % (kw['star'],kw['comment'])
        task_obj.sudo().message_post(body=customer_msg)
        return http.request.render("project_task_issue_rating.successful_review_custom_task")
    
    # @http.route(['/customer_feedback_rating/feedback/<int:issue_id>'], type='http', auth='user', website=True)
    # def feedback_issue_email_custom(self, issue_id, **kw):
    #     issue_obj = request.env['project.issue'].sudo().browse(issue_id)
    #     values = {
    #         'message' : issue_obj.request_issue,
    #         'project':  issue_obj.project_id.name,
    #         'issue':  issue_obj.name,
    #         'customer' : issue_obj.partner_id.name,
    #         }
    #     values.update({'issue_id': issue_id})
    #     return request.render("project_task_issue_rating.issue_feedback", values) 
    
    # @http.route(['/project_issue/feedback_custom/'],type='http', auth='public', website=True)
    # def start_issue_rating_customs(self, **kw):
    #     partner_id = kw['partner_id']
    #     issue_obj = request.env['project.issue'].sudo().browse(int(kw['issue_id']))
    #     vals = {
    #           'rating':kw['star'],
    #           'comment':kw['comment'],
    #         }
    #     issue_obj.sudo().write(vals)
    #     customer_msg = _(issue_obj.partner_id.name +" "+'has send this feedback rating is %s and comment is %s') % (kw['star'],kw['comment'])
    #     issue_obj.sudo().message_post(body=customer_msg)
    #     return http.request.render("project_task_issue_rating.successful_feedback")
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
