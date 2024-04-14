# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Project and Project Task Unique Sequence Number",
    'license': 'Other proprietary',
    'price': 29.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """Project Task Unique Number Sequence and Project Sequence Number.""",
    'description': """
This app will automatically generate a unique sequence number for project and project
tasks as shown in the below screenshots.
""",
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/project_task_issue_sequence_number/1251',
    'version': '9.2.2',
    'category' : 'Services/Project',
    'depends': [
                'project',
#                 'project_issue',
                ],
    'data':[
        'data/project_sequence.xml',
        'views/project_view.xml',
        'views/project_task_view.xml',
#         'views/project_issue_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
