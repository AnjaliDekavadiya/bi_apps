# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

{
    'name':'Fleet Vehicle Inspection Management',
    'price': 49.0,
    'version':'8.2.35',
    'category': 'Human Resources/Fleet',
    'currency': 'EUR',
    'summary': 'Allow you to manage periodic inspection of fleets or vehicles along with reminder.',
    'license': 'Other proprietary',
    'description': """
This module create fleet Safety Inspection
fleet app
fleet inspection
vehicle inspection
safety inspection
Fleet Vehicle Inspection Management
odoo fleet app
fleet module
fleet app
            """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'images': ['static/description/image.jpg'],
    'support': 'contact@probuse.com',
    # 'live_test_url': 'https://youtu.be/lCNvyXg8eps',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/fleet_safety_inspection/255',# 'https://youtu.be/nCr9I982LiA',
    'depends': [
        'fleet',
        'uom',
        'mail',
    ],
    'data':[
        'data/request_cron.xml',
        'data/inspection_request_sequence.xml',
        'data/mail_template_data.xml',
        'security/safety_security.xml',
        'security/ir.model.access.csv',
        'wizard/create_service_view.xml',
        'views/vehicle_inspection_view.xml',
        'views/fleet_view.xml',
        'views/vehicle_inspection_report.xml',
        'views/vehicle_inspection_line_view.xml',
        'views/inspection_request_view.xml',
    ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
