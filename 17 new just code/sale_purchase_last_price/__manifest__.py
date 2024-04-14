# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sale Order and Purchase Order Last/Previous Order Price',
    'version': '5.1.33',
    'category' : 'Sales',
    'price': 9.0,
    'currency': 'EUR',
    'summary': """Fetching last order price in Sales order and Purchase order.""",
    'description': """ 
sale order price
purchase order price
last order price
last price
previous price
order price
previous order price
price history    
    """,
    'license': 'Other proprietary',
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/sale_purchase_last_price/894',#'https://youtu.be/PEiTyXKO3Os',
    'images': ['static/description/img1.png'],
    'depends': [
        'sale',
        'sale_management',
        'purchase'
    ],
    'data':[
        'views/purchase_views.xml',
        'views/sale_views.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


