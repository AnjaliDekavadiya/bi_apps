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
    'name': 'Amount In Words',
    'version': '17.0.1.0',
    'sequence': 1,
    'category': 'Accounting',
    'description':
        """
odoo Apps will show total amount into words in Sale, Purchase, Invoice

Amount is words

Odoo amount in words

Print Total amount into words in odoo

Print total amount in words

Total amount

Total amount in words

Invoice amount in words

Odoo invoice amount in words

Print invoice amount in words

Odoo print invoice amount in words

Display  Total Amount In Words

Odoo Display  Total Amount In Words

Print amount with words without cents

Odoo Print amount with words without cents

Print amount with words including cents

Odoo Print amount with words including cents

Amount in Words for Invoice

Odoo Amount in Words for Invoice

Total amount in words

Odoo total amount in words

Print total amount in words

Odoo print total amount in words

Amount in words for Indian Accounting

Odoo Amount in words for Indian Accounting

POS total amount to words

Odoo POS total amount to words

Display invoice amount 

Odoo display invoice amount in words

Amount with words

Odoo Amount with Words

Manage Amount with Words

Odoo manage Amount with Words

Display Amount

Odoo Display Amount

Manage Display Amount

Odoo Manage Display Amount

Display Amount In Words in Sale

Odoo Display Amount In Words in Sale

Display Amount In Words in Purchase

Odoo Display Amount In Words in Purchase

Display Amount In Words in Invoice

Odoo Display Amount In Words in Invoice

Manage Display Amount In Words in Sale

Odoo Display Amount In Words in Sale

Display Amount In Words in Purchase

Odoo Display Amount In Words in Purchase

Display Amount In Words in Invoice

Odoo Display Amount In Words in Invoice

visible or invisible Amount

odoo visible or invisible Amount

manage visible or invisible Amount

odoo Manage visible or invisible Amount

print Amount

odoo Print Amount

manage Print Amount

odoo Manage Print Amount


    """,
    'summary': 'odoo Apps will show toatl amount into words in Sale, Purchase, Invoice, amount in words,  amount in words',
    'depends': ['sale_management','account','purchase'],
    'data': [
        'view/sale_order_view.xml',
        'view/purchase_order_view.xml',
        'view/invoice_view.xml',
        'report/report_view.xml'
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
    'price':25.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
    'pre_init_hook' :'pre_init_check',
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
