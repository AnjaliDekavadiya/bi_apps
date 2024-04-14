# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full
# copyright and licensing details.
{
    'name': "Job Inspection for Car Repair Requests",
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """Job Inspection process of your car repair requests.""",
    'price': 70.0,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/car_repair_job_inspection/437',#'https://youtu.be/tB-n692j0Zo',
    'version': '7.4',
    'description': """
car Repair Job Inspection.
Allow you to have inspection process of your car repair request.
car repair
job inspection
car repair job inspection
car inspection
""",
    'category' : 'Services/Project',
    # any module necessary for this one to work correctly
    'depends': ['car_repair_maintenance_service'],
    'installable' : True,
    'application' : False,
    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/inspection_sequence.xml',
        'report/inspection_report.xml',
        'views/car_repair_inspection_record_view.xml',
        'views/car_repair_inspection_result_view.xml',
        'views/car_repair_inspection_type_view.xml',
        'views/car_repair_order_inspection_view.xml',
        'views/car_repair_order_inspection_line_view.xml',
        'views/car_project_view.xml',
        'views/car_job_order_view.xml',
        'views/car_repair_support_view.xml',
    ],
}
