# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Sales Quotation Number",
    'license': 'Other proprietary',
    'price': 19.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """Generate sales quotation number for sales quotations.""",
    'description': """
This module will generatesales quotation Sequence's quotation wise Unique Number.
sales quotation number
sale quote number
sales quote number
sale quotation number
""",
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/image.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/odoo_sales_quotation_number/129',#'https://youtu.be/l9FB3n_PNhU',
    'version': '6.1.3',
    'category' : 'Sales',
    'depends': [
                'sale',
                ],
    'data':[
        'data/sales_quotation_sequence.xml',
        'views/sale_order_view.xml',
        'report/sale_order_report.xml',
        'report/sale_report_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
