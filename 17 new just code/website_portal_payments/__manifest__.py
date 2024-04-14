# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Website Customer/Supplier Portal Show Payments",
    'price': 19.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """Allow customer/supplier to login in My Account and view Payments and Print Receipts.""",
    'description': """
Website Customer/Supplier Portal Show Payments
This module show Payment Receipt on My Account.
Allow customer/supplier to login in My Account and view Payments and Print Receipts.
Print Payment Receipts
Payment Receipt on Portal
customer portal payment
customer portal receipts
customer view portal
supplier portal payment
supplier payment receipt
portal customer 
portal supplier
Print Sales Receipts and Purchase Receipts
Sale receipt
purchase receipt
Print Vouchers
Print Account Voucher
portal
    Account Payment Report
- Customer Payment Receipt Report
- Print receipt
- Print Payment
Customer Payment Receipt Report
                
- Payments report
payment receipt
payment customer receipt
payment voucher
print payment order
print payment customer
print customer payment
customer voucher
customer bill
print customer voucher
print customer bill
print pdf payment
Invoice Payment Receipt Report:
- Creating Invoice Payment Receipt Report
- Sent payment receipt to customer by email.
- Customer payment receipt odoo 9 
- Invoice payment receipt
- Invoice  payments.
payment receipt
payment invoice receipt
invoice payment receipt
invoice report
payment receipt
print voucher
voucher report
voucher receipt
supplier payment receipt
invoice payment receipt
Payment receipt print odoo
odoo receipts
invoice report receipt
payment report
customer payment report
customer payment receipt
supplier payment receipt
my account page
my account login
my account portal page
my account customer payment
your invoices and payments
your invoices
your payments
your receipts
customer receipts
customer print receipts
view portal payment accounting
account payment on portal
account payment on customer portal
payment on portal
odoo_website_portal_payment
Website Portal Payments
receipt of all invoices from My Account
Generated Payment Receipt
How do we get Payment receipt

Website Portal Payment module

    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img.png'],
    'version': '8.2.1',
    'category' : 'Website/Website',
    'depends': [
#         'website_portal_sale',
        'sale', #odoo11
        'account',
        'website',
    ],
    # 'live_test_url': 'https://youtu.be/H22djqzAO0k',
    # 'live_test_url':'https://youtu.be/lP2vmu6xxUQ ',
    'live_test_url' : 'https://probuseappdemo.com/probuse_apps/website_portal_payments/373',#'https://youtu.be/hHiwY1cHtwg ',
    'data':[
        'security/ir.model.access.csv',
        'security/portal_payment_security.xml',
        # 'views/payment_report_reg.xml',
        # 'views/payment_report_view.xml',
        'views/website_portal_sale.xml',
    ],
    'installable' : True,
    'application' : False,
    'auto_install' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
