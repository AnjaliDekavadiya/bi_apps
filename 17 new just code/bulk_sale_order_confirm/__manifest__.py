# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Bulk Sales Order Confirm",
    'currency': 'EUR',
    'price': 9.0,
    'images': ['static/description/img.jpg'],
    #'live_test_url': 'https://youtu.be/SBls3tCZkwk',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/bulk_sale_order_confirm/82',#'https://youtu.be/3NG53lOOB34',
    'license': 'Other proprietary',
    'summary': """Allows you to confirm multiple sale orders in bulk.""",
    'description': """
This module allows you to confirm a bulk sale orders and sent confirm mail.
bulk sales order confirm
bulk sale order confirm
bulk sale orders confirm
confirm sales order
sales order confirm
sale order confirm
mass sales order confirm
mass sale order confirm

    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'version': '6.1.2',
    'category' : 'Sales/Sales',
    'depends': [
        'sale_management',
        'sale_stock' #'sale stock' dependency it's not mandatory this dependency add for show 'delivery' smart button on sales orders.
    ],
    'data':[
        'security/ir.model.access.csv',
        'wizard/bulk_sale_order_confirm_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
