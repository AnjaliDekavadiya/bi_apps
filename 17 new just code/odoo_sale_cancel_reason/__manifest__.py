# -*- coding:utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Sale Cancel Reason and Reason Details',
    'version': '5.1.2',
    'price': 19.0,
    'website': 'www.probuse.com',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category': 'Sales/Sales',
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'summary':  """Cancel Reason on Sales Order Cancel Button""",
    'description': """
Sale Order Cancel Reason
sale cancel
sales cancel reason
sales cancel order
sales order cancel
sale order cancel
cancel reason
sale reason
cancel reason sales
quote cancel reason

    """,
    'images': ['static/description/img1.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/odoo_sale_cancel_reason/1046',#'https://youtu.be/YV3EWEaRHCI',
    'support': 'contact@probuse.com',
    'depends': ['sale'],
    'data': [
        'data/sale_cancel_mail.xml',
        'security/ir.model.access.csv',
        'views/sale_cancel_reason_view.xml',
        'wizard/sale_order_cancel_views.xml',
        'views/sale_view.xml',
    ],
    'installable' : True,
    'application' : False,
    
}




