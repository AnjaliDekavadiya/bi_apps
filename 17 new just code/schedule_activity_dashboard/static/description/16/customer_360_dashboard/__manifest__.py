# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Customer 360 Dashboard",
    'version': '6.2.8',
    'category': 'Sales/Sales',
    'license': 'Other proprietary',
    'price': 99.0,
    'currency': 'EUR',
    'summary':  """Customer 360 Dashboard in Odoo.""",
    'description': """
Customer 360 Dashboard
customer dashboard
customer view
customer 360 board
customer 360 view
customer kanban
    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/img.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/customer_360_dashboard/726',#'https://youtu.be/7gxFjcK3voo',
    'depends': [
        'crm',
        'sale_management',
        'project',
    ],

    'data': [
        'views/customer_360_dashboard_view.xml',
    ],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
