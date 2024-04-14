# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': "Sales Estimate from Car Repair Request",
    'version': '6.1.6',
    'price': 49.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "www.probuse.com",
    'support': 'contact@probuse.com',
    'summary': 'This module allow you to create sales estimate and send to customer for car repair request.',
    'description': """
This module create and send estimate to customer.
car repair
job estimate
sales estimate
car repair request
customer estimate
estimation
estimate car
    """,
    'category': 'Sales/Sales',
    'images': ['static/description/image.jpg'],
    # 'live_test_url': 'https://youtu.be/sRSgfnaKZrk',
    'live_test_url' : 'https://probuseappdemo.com/probuse_apps/car_repair_estimate/387',#'https://youtu.be/FQVYPCkDWfo',
    'depends': ['odoo_sale_estimates', 'car_repair_maintenance_service'],
    'data': [
        'security/ir.model.access.csv',
        'security/estimate_security.xml',
        'report/sale_estimate_report.xml',
        'wizard/car_repair_support_wizard_view.xml',
        'views/car_repair_support_view.xml',
        'views/sale_estimate_view.xml',
    ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

