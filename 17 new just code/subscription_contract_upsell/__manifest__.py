# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Upsell on Subscription / Contract / Recurring",
    'price': 99.0,
    'version': '5.1.4',
    'category': 'Sales',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This app allow you to make upsell on contract / subscription.""",
    'description':  """
Odoo Subscription Contract Upsell
Upsell
customer upsell
contract Upsell
subscription Upsell
sale Upsell
Upsell sale
Recurring Invoice
contract_recurring_invoice_analytic
Odoo Sales Contract
Recurring
Warranty
contract Warranty
subscription
contract management
contract invoice
Recurring invoice
maintenance invoice
yearly contract
Sales Contract Subscription and Recurring Invoice
Sales Contract Subscription
Recurring Invoice
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
                    
                    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/subscription_contract_upsell/936',#'https://youtu.be/ZpjeB8T6AE4',
    'images':   [
        # 'static/description/img1.jpg'
        'static/description/sales_contract.jpg'
                        ],
    'depends':  [
        'contract_recurring_invoice_analytic',
        'sale',
                        ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/subscription_contract_upsell_view.xml',
        'views/account_analytic_account_view.xml',
        'views/sale_order_view.xml',
            ],
   'installable' : True,
   'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
