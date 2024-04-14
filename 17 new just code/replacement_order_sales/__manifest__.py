# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Replacement Order for Sales Process",
    'version': '5.1.2',
    'license': 'Other proprietary',
    'price': 19.0,
    'currency': 'EUR',
    'summary':  """This app allows your sales team to create a replacement order for sales orders.""",
    'description': """
Replacement Order for Sales Processs
Replacement Reasons
replacement orders
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img33.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/replacement_order_sales/675',#'https://youtu.be/mXx40gPfMvY',
    'category': 'Sales/Sales',
    'depends': [
                'sale_management',
            ],
    'data': [
         'security/ir.model.access.csv',
         'data/ir_sequence_data.xml',
         'views/sale_view.xml',
         'views/replacement_reason_views.xml',
         'views/sale_report_template_view.xml',
         'report/sale_report_view.xml',
            ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
