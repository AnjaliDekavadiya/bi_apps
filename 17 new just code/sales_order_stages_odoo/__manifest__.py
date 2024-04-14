# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.
{
    'name': 'Sales Order Stages / Sales Stages',
    'version': '6.1.2',
    'price': 12.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'depends': [
        'sale',
    ],
    'category': 'Sales/Sales',
    'summary':  """Sales Stages on Sales Order""",
    'description': """
This app allows you to manage sale order stages.
sales stage
sale stage
sales order stage
sale order stage

    """,
    
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'images': ['static/description/ss66.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/sales_order_stages_odoo/1020',#'https://youtu.be/Kzfzg4V8dd0',
    'data': [
        'security/ir.model.access.csv',
        'views/sale_stage_view.xml',
        'views/sale_view.xml',
        'report/sale_report_view.xml',
    ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
