# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Quality Check and Alert Management on Tasks',
    'version': '5.1.15',
    'license': 'Other proprietary',
    'price': 99.0,
    'currency': 'EUR',
    'category' : 'Project',
    'summary': """Allow Quality Check Management on Project Tasks along with Quality Control Points and Alerts.""",
    'description': """
Allow Quality Check Management on Project Tasks along with Quality Control Points and Alerts
quality check
quality control
quality alerts
alert quality
alerts quality
quality control points
control  point
control points
task quality management
task quality
project quality
project task quality
quality check task
task quality check
checklist
quality checklist
alerts
task alerts
task warnings
project warnings
    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/project_task_quality_management/660',#'https://youtu.be/ZC0wi4jBVTk',
    'depends': [
        'project',
    ],
    'data':[
        'security/quality_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'wizard/quality_check.xml',
        'wizard/quality_alert.xml',
        'report/project_quality_check.xml',
        'report/project_quality_control_point.xml',
        'report/project_quality_alert.xml',
        'views/project_quality_check_view.xml',
        'views/project_quality_control_point_view.xml',
        'views/project_quality_team_view.xml',
        'views/quality_type_view.xml',
        'views/project_quality_alert_view.xml',
        'views/project_task_view.xml',
        'views/quality_tag_view.xml',
        'views/quality_reason_view.xml',
        'views/menu_item.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
