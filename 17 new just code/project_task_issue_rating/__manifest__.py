# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Project Task Review and with Ratings",
    'price': 49.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This module allow project manager to give review on task and rating.""",
    'description': """
This app allows your project managers to send review requests to your customer for task work by project users. We have added a button on the task form which will allow them to
send a review request to the customer by email using wizard.
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/display.jpg'],
    'version': '6.1.3',
    'category' : 'Services/Project',
    'depends': [
            'project',
            'website'
    ],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/project_task_issue_rating/334',#'https://youtu.be/hmSpdPH-NPM',
    'data':[
            'security/ir.model.access.csv',
            'wizard/wizard_of_review.xml',
            'data/task_mail_template.xml',
            # 'data/issue_mail_template.xml',
            # 'wizard/issue_wizard.xml',
            'views/project_view.xml',
            # 'views/issue_feedback_template.xml',
            'views/task_feedback_template.xml',
            'views/thankyou_template.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
