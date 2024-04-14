# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Mass Cancel Sales Order and Purchase Order',
    'version': '5.1.15',
    'price': 29.0,
    'currency': 'EUR',
    'category': 'Sales/Sales',
    'license': 'Other proprietary',
    'summary': 'Allow you to Mass Cancel Sales Order and Purchase Order',
    'description': """
allow to cancel your sale orders
Mass Cancel Sales Order and Purchase Order
cancel sales order
cancel sale order
mass cancel
mass cancel sales order
mass sales order cancel
mass sale order cancel
mass purchase order cancel
mass purchase cancel
mass sales cancel
mass sale cancel
mass purchase orders cancel
mass cancelling
cancel sales
cancel purchase
cancel sales order
cancel sale order
cancel sale
cancel purchase order
cancel purchases order
cancel purchase order

""",
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'https://www.probuse.com',
    'images': ['static/description/img1.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/mass_cancel_sale_purchase_order/979',#'https://youtu.be/cxy24hdmWPw',
    'depends': [
        'sale_management',
        'sale_stock',
        'purchase_stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/cancel_sale_order_view.xml',
        'wizard/cancel_purchase_order_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
