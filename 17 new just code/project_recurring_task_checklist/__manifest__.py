# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. 
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Template Based Recurring Tasks and Checklists',
    'version': '5.1.5',
    'price': 99.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website' : 'www.probuse.com',
    'summary':  """Recurring Tasks and Checklist Tasks in Odoo Project App""",
    'description': """
task recurring
recurring task
project recurring task
checklist tasks
task checklists
task checklist
project task recurring
task template
checklist template
     """,
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'], 
    'depends': [
        'project',
    ],
    'data': [
       'data/recurring_task_cron.xml',
       'security/ir.model.access.csv',
       'views/project_task_view.xml',
       'views/hr_project_task_menu_view.xml',
       'views/recurring_task_view.xml',
     ],
    'category': 'Project',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/project_recurring_task_checklist/814',#'https://youtu.be/Oc85VrOekDY',
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
