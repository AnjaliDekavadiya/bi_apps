# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Website Wallet for Customers',
    'version': '5.6.1',
    'currency': 'EUR',
    'price': 49.0,
    'depends': [
        'website_sale',
        'sale_management',
    ],
    'license': 'Other proprietary',
    'category': 'Website/Website',
    'summary': 'This app provide wallet feature to your website where customer can add and withdraw from wallet for shopping.',
    'description': """
Website Wallet
customer_website_wallet
website_wallet
Odoo Website wallet
Website Wallet
odoo_e_wallet
e-wallet
digital wallet
Odoo Website Wallet
Wallet Recharge
User Wallet Credit
balance of the wallet
wallet balance
customer balance
wallet balance
Wallet Transaction
Use Wallet
Wallet Amount
website payments
website payment
wallet payment method
using wallet
User Wallet Credit
Add Wallet Credit
Pay using Wallet
Wallet Transaction .
            """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/customer_website_wallet/1271',
    #'live_test_url': 'https://youtu.be/xKveF8Ulc-A',
#    'live_test_url': 'https://youtu.be/g__9R57Gus0',
    'data': [
        'security/ir.model.access.csv',
        'security/customer_wallet_security.xml',
        'data/mail_template.xml',
        'data/sequence.xml',
        'data/product_demo.xml',
        'data/low_balance_template.xml',
        'views/wallet_transfer_template.xml',
        'views/customer_wallet_view.xml',
        'views/wallet_template.xml',
        'views/res_partner_view.xml',
        'views/product_template_view.xml',
        'views/sale_order_view.xml',
        'data/wallet_acquire_date.xml',
     ], 
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
