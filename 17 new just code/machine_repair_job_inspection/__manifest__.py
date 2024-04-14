# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Job Inspection for Machine Repair Requests',
    'version': '8.1.5',
    'category' : 'Services/Project',
    'depends': [
        'machine_repair_management',
    ],
    'price': 59.0,
    'license': 'Other proprietary',
    'currency': 'EUR',
    'summary': """Job Inspection process of your machine repair requests.""",
    'description': """
Machine Repair Job Inspection.
Allow you to have inspection process of your machine repair request.
machine repair
job inspection
machine repair job inspection
machine inspection
""",
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/machine_repair_job_inspection/463',#'https://youtu.be/ucsXkig-t0I',
    'data':[
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/inspection_sequence.xml',
        'report/inspection_report.xml',
        'views/repair_inspection_view.xml',
        'views/repair_inspection_record_view.xml',
        'views/repair_inspection_line_view.xml',
        'views/job_order_view.xml',
        'views/repair_inspection_result.xml',
        'views/repair_inspection_type_view.xml',
        'views/project_view.xml',
        'views/machine_repair_support_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
