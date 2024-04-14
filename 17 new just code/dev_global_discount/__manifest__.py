# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################
{
    "name": "Sale,Purchase & Invoice Discount with Accounting Entries",
    "category": 'Sales',
    "sequence": 1,
    "version": '17.0.1.0',
    "summary": """
                 odoo Apps will set global Fixed/Percentage discount in Sale, Purchase, Invoice with accounting Entries., Global discount, fixed discount, Percentage discount, sale discount, purchase discount, Invocie discount, Accounting entreis discount
                 
        """,
    "description": """
        
        odoo Apps will set global Fixed/Percentage discount in Sale, Purchase, Invoice with accounting Entries.

Sale purchase invoice discount with accounting entries
Global sale purchase invoice discount
Global sale purchase discount odoo
Sale purchase invoice discount with accounting entries
Apply discount on total sales order
Apply discount on total Purchase order.
Apply discount on total Invoices.
Both Fixed and percentage method can be work out.
Discount account Setup & Generate Accounting Entries.
Sale invoice discount entries 
Purchase invoice discount entries
Sales invoice discount entries oddo
Purchase invoice entries oddo
Sale,Purchase & Invoice Discount with Accounting Entries & Limits
Create sales invoice discount entry
Create purchase invoice discount entry
Create sales invoice discount accounting entry
Create purchase invoice discount Accounting entry
Odoo Create sales invoice discount entry
Odoo Create purchase invoice discount entry
Odoo Create sales invoice discount accounting entry
Odoo Create purchase invoice discount Accounting entry
        
    """,
    "depends": ['sale','account','purchase'],
    "data": [
        'views/account_account_view.xml',
        'views/sale_order_view.xml',
        'views/purchase_order_view.xml',
    ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    #author and support Details
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':39.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
    "license":"LGPL-3",
    "pre_init_hook" :"pre_init_check",
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
