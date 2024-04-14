# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Search by Products in POS Orders',
    'version': '5.2.3',
    'license': 'Other proprietary',
    'price': 9.0,
    'currency': 'EUR',
    'summary':  """POS Order Search by Product.""",
    'description': """
Search By Product POS Order
POS Orders search product
search by product pos orders
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img251.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/search_by_product_pos_order/888',#'https://youtu.be/xD7i67RABwI',
    'category': 'Sales/Point Of Sale',
    'depends': ['point_of_sale'],
    'data': [
         'views/pos_order_views.xml',
            ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
