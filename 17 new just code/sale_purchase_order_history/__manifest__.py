# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Sale and Purchase Order History',
    'version': '5.12.5',
    'price': 9.0,
    'category' : 'Sales',
    'license': 'Other proprietary',
    'currency': 'EUR',
    'summary': """Sales order and Purchase Order History (Last 10 Orders)""",
    'description': """
sales history
purchase history
sale history
purchase history
sale order history
purchase order history    
    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/sale_purchase_order_history/895',#'https://youtu.be/1bbDRVUqZBk',
    'images': [
               'static/description/image.png'
               ],
    'depends': [
        'sale',
        'sale_management',
        'purchase'
    ],
    'data':[
        'views/sale_order_view.xml',
        'views/purchase_order_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
