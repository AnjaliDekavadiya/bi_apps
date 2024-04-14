# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Cash On Delivery on Website Ecommerce Shop',
    'version': '6.3.0',
    'price': 149.0,
    'currency': 'EUR',
    'category': 'Website/Website',
    'license': 'Other proprietary',
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website' : 'www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpeg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/website_cash_on_delivery/962',#'https://youtu.be/4QNL6AMqQZs',
    'depends': [
                'website_sale',
                'sale_management',
                'account',
                'stock',
                'payment',
                ],
    'data': [
        'security/ir.model.access.csv',
        'security/cashondelivery_security.xml',
        'views/cod_transfer_template.xml',
        'data/cod_acquire_data.xml',
        'views/product_view.xml',
        'views/payment_acquire_view.xml',
        'views/website_sale_template.xml',
        'views/sale_view.xml',
        'views/cashondelivery_view.xml',
        'views/partner_view.xml',
        'report/cash_on_delivery_collection_report.xml',
            ],
    'summary':  "Allow your customer to choose Cash on Delivery Option on Odoo Shop Payment",
    'description': """
Website Cash on Delivery
Website Cash on Delivery
Cash on Delivery Website
Cash on Delivery
Cash On Delivery Collection
Cash on Delivery Available on Product
Cash on Delivery Not Available on Product
Cash on Delivery Available between on Minimum Order Amount and Maximum
Cash on Delivery Available on Minimum Order Amount
COD on website
Website Cash on delivery collection
cash on delivery
cod
website cash on delivery
shop cash on delivery
ecommerce cash on delivery
website shop cash on delivery
cash on delivery on website
cash on delivery website
cash on delivery shop
customer cash on delivery
product cash on delivery
item cash on delivery
odoo cash on delivery
cash on delivery odoo
website shop
Payment Acquire
payment method
cash payment method
cash payment
cash delivery
customer delivery
shop cod
cod shop
Payment Acquire cash on delivery
cash on delivery paymnent method
COD
website customer payment
website portal payment
odoo cod
collections
collection
cash collection

    """,
    'assets': {
        'web.assets_frontend': [
            'website_cash_on_delivery/static/src/js/website_sale.js',
        ]
    },
    'installable': True,
    'application': False,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
