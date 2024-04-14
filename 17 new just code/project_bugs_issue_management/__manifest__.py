# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Issues / Bugs Management for Project Tasks',
    'version': '8.1.3',
    'price': 99.0,
    'category' : 'Services/Project',
    'license': 'Other proprietary',
    'currency': 'EUR',
    'summary': """Project Tasks Bugs and Issues Management.""",
    'description': """
This app allows your project team to create an issue for a task of a project. Allow your team to manage issues and bugs of project and tasks.
Allow your team to create an issue for a task.
After creating an issue assigned to the user.
This app allows tracking of issues.
Allow your customers to view issues on portal of your website.
For more details please check below screenshots and watch the video.
project issue
project bugs
task bugs
bugs
task issues
issue task
bug task
    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    # 'live_test_url': 'https://youtu.be/QurlTBzAPrA',
    'live_test_url' : 'https://probuseappdemo.com/probuse_apps/project_bugs_issue_management/186',#'https://youtu.be/85PM7-OO_eo',
    'images': [
        'static/description/img.jpg'
    ],
    'depends': [
        'project',
        'website'
    ],
    'data':[
        'security/ir.model.access.csv',
        'data/custom_issues_type_data.xml',
        'report/project_report_view.xml',
        'wizard/create_bug_issues_view.xml',
        'views/project_task_view.xml',
        'views/issues_type_view.xml',
        'views/project_portal_templates.xml',
        'views/menu.xml',
    ],
    'qweb': [
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
