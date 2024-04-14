# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Bundle of Project Related Apps",
    'version': '3.1.4',
    'price': 1.0,
    'currency': 'EUR',
    'category' : 'Project/Project',
    'license': 'Other proprietary',
    'summary': """This module contains bundle of Project Related Apps/Modules.""",
    'description': """
Project apps
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/prjb.jpg'],
    'depends': [
        'odoo_project_phases',
        'odoo_project_task_import',
        'odoo_task_project_template',
        'print_project_report',
        'project_bugs_issue_management',
        #'project_meeting_minutes',
        'project_profit_loss_report',
        'project_recurring_task_checklist',
        'project_stage_responsible_user',
        'project_stages_odoo',
        'project_task_images_photos',
        'project_task_issue_rating',
        'project_task_issue_sequence_number',
        'project_task_notes',
        'project_task_quality_management',
        'project_task_user_reminder_email',
        'project_task_work_instruction',
        'project_team_odoo',
    ],
    'data':[
        
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
