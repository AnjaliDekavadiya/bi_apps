# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full
# copyright and licensing details.
{
    'name': "Website Portal Account Customer Statement",
    'currency': 'EUR',
    'price': 49.0,
    'depends': [
        #'website',
        'portal',
        'account_customer_statement',
    ],
    'license': 'Other proprietary',
    'summary': """Allow your customer to print statements from website account page.""",
    'description': """
customer portal payment
customer portal receipts
customer view portal
portal customer
Customer Statement Ledger
portal
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
website customer statement
portal customer statement
my account customer statement
website partner statement
portal partner statement
my account partner statement
Customer/Supplier Statement
Customer Overdue Payments
Customer/Supplier Statement and Customer Overdue Payments offers you to view customers or suppliers invoice or overdue invoices details and mail customers that details
account customer statement
customer_overdue_statement
account_statement
customer statement
Account Customer/Supplier Statement
Printing Customer Statement Details
You Can Print Customer Statement Report From The Above Customer Form in Partner Form View
Sending Customer Statement Details
You Can Send Customer Statement To Relevent Customer.
customer ledger
customer statement report
partner statement
partner ledger
customer ledger
supplier ledger
receivable statement
partner ledger enterprise
partner ledger filter
print partner ledger by customer
print partner ledger by supplier
print partner ledger by vendor
partner ledget option to print by partner
partner ledger
overdue customer
customer overdue
overdue payment report
overdue payment
Customer/Supplier Statements
Supplier Statements
Customer Statements
Partner wise Ledger Report
customer ledger
Customer Statement
Account Statements
Account Statement
Overdue Payments/Statement
Overdue Payments
Overdue Statement
supplier ledger
account statement
partner statement
customer statement

    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/cimg1.jpg'],
    'version': '7.6.1',
    'category': 'Website/Website',
    # 'live_test_url': 'https://youtu.be/lSDhS2A1rYg',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/portal_account_customer_statement/641',#'https://youtu.be/Ep_LZtj5KX4',
    'data': [
        'views/website_portal_sale.xml',
        'report/report_partnerledger.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
