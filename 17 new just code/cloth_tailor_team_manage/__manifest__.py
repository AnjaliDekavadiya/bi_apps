# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Cloth Tailor with Team Manage',
    'version' : '5.1.3',
    'price' : 19.0,
    'currency': 'EUR',
    'category': 'Sales/Sales',
    'license': 'Other proprietary',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/cloth_tailor_team_manage/198',#'https://youtu.be/7SrfJEnnOd0',
    'images': [
        'static/description/img.jpg',
    ],
    'summary' : 'This app allows you to manage tailor requests with a tailor team.',
    'description': """
This app allows you to manage tailor requests with a tailor team as shown in below screenshots.
    - Add a Tailor Teams menu under configuration.
    - Add ‘Team’ field on tailor request form view.
    - Tailor Team field show on tailor request report pdf.
    - Team field show on my account tailor request to customers.
    - For more details please check below screenshots and watch the video.
    """,
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website' : 'www.probuse.com',
    'depends' : [
        'cloth_tailor_management_odoo'
    ],
    'support': 'contact@probuse.com',
    'data' : [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/tailor_team_view.xml',
        'views/cloth_request_details_view.xml',
        'views/project_task_view.xml',
        'views/template.xml',
        'report/cloth_request_report_template.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
