# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Task Template and Project Template',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'price': 49.0,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'summary' : 'This app allow you to create Project Task Template and Project Template',
    'support': 'contact@probuse.com',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/odoo_task_project_template/1054',#'https://youtu.be/SlqRMBfheu8',
    'description': """
Task Template and Project Template
This app allow you to create Project Task Template and Project Template
project template
task template
project task template
template task
template project
""",
   'images': ['static/description/img1.jpg'],
    'version': '5.1.6',
    'category' : 'Operations/Project',
    'depends': [
                'project',
                ],
    'data':[
        'views/project_template_view.xml',
        'views/task_template_view.xml',

    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:





