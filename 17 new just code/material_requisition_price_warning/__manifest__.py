# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Product/Material Requisitions Cost Price and Warning',
    'version': '5.1.9',
    'price': 59.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This module allow your employees/users to Material Requisitions Price and Warning.""",
    'description': """
Material Requisitions Price by Employees/Users
material requisition
product requisition
Material Requisitions Cost Price
Material Requisitions Warning
    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/image1.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/material_requisition_price_warning/692',#'https://youtu.be/nb1fY6Xn3Ys',
    'category': 'Sales',
    'depends': [
                'material_purchase_requisitions',
                ],
    'data':[
        'report/purchase_requisition_report.xml',
        'views/purchase_requisition_view.xml',
        'views/hr_employee_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
