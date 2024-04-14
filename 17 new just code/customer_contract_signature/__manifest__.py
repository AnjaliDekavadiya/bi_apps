# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Customer Signature on Contract/Subscription",
    'version': '5.1.6',
    'price': 99.0,
    'category': 'Sales',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """ This app allow your customers to do signature on contract from website portal my account. """,
    'description':  """
Signature of Customer on Contract
Allow your customer to sign on contract & View sign on portal
Customer will get mail for signature request and can do signature on contract on website portal
Once customer sign on contract he/she will get response and thank you mail from system
Customer can view signature on portal
customer digital signature
customer sign
customer signature
client signature
contract sign
sign contract
contract signature
Recurring
Warranty
contract Warranty
maintenance Warranty
maintenance contract
maintenance analytic account
maintenance subscription
subscription
contract management
contract invoice
Recurring invoice
maintenance invoice
yearly contract
contract customer
customer contract
analytic account
subscription contract
subscription management
customer recurring invoice
community subscription
community version
Sales Contract and Recurring Invoice
subscription
client subscription
customer subscription

    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/customer_contract_signature/876',#'https://youtu.be/hC58dL53Yso',
    'images':   [
        'static/description/img1.jpg'
    ],
    'depends':  [
        'contract_recurring_invoice_analytic',
        'subscription_contract_customer_portal',
        'website',
        'portal',
    ],
    'data': [
        # 'data/send_thankyou_mail.xml',
        # 'data/send_signature_request_email.xml',
        'data/send_thankyou_mail_new.xml',
        'data/send_signature_request_email_new.xml',
        'views/analytic_account_view.xml',
        'views/analytic_account_customer_signature_template.xml',
    ],
    'installable' : True,
    'application' : False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
