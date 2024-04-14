# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Fleet Services Integrate with Job Orders',
    'version': '7.1.4',
    'currency': 'EUR',
    'price': 29.0,
    'license': 'Other proprietary',
    'category': 'Human Resources/Fleet',
    'summary': 'Create Job Order / Work Order from Fleet Services',
    'description': """
fleet app
fleet management
fleet service
fleet jobs
job order
work order
job orders
fleet app
Fleet Vehicle Inspection Management
odoo fleet app
fleet module
fleet app
service job order
service work orders
service task
fleet task
fleet project
task fleet
vehicle task
""",
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'depends': ['fleet','project'],
    'support': 'contact@probuse.com',
    # 'live_test_url': 'https://youtu.be/Qdq2ud1p1R0',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/fleet_job_work_orders/256',#'https://youtu.be/0aQGNcKbdaA',
    'images': ['static/description/image.png'],
    'data': [
              'security/ir.model.access.csv',
              'views/fleet_log_service_inherit.xml',
              'wizard/create_joborder_view.xml',
             ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

