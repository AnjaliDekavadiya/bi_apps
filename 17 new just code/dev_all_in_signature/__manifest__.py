# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://devintellecs.com>).
#
##############################################################################
{
    'name': 'All In One Digital Signature - Purchase Order, Invoice & Delivery',
    'version': '1.0',
    'sequence': 1,
    'category': 'Extra Tools',
    'description': """
    
This module useful to give digital signature features in the purchase order/request for quotation, invoice /bill. Digital signature useful for approval, security purpose, contract, etc. We have another feature for other sign option so you can add details like sign by. You can print a report with a digital signature and other information.

The Odoo Digital Signature App enables you to effortlessly add signatures by uploading a file or drawing directly within the Odoo app. It offers a smarter way to handle your documents, taking your business processes to the next level. Easily integrate digital signatures into crucial documents such as purchase orders, invoices, picking orders, and even print signatures in responsive reports. With its user-friendly interface, this app ensures a smooth and paperless workflow for enhanced efficiency in your operations.
               
Digital signature purchase order Digital sign RFQ purchase order Digital Signature request for quotation Digital Signature RFQ Digital Signature PO Digital Signature Odoo Digital Signature Purchases digital signature sale order Module digital sign purchase order digital sign invoice digital sign bill digital signature sales digital sign RFQ digital sign account Odoo Purchase digital sign on purchase order digital sign in purchase digital sign on purchase report purchase order digital signature on purchase digital signature on purchase order digital signature on rfq digital signature quote digital signature on quote
    """,
    
    'summary': 'Digital signature purchase order Digital sign RFQ purchase order Digital Signature request for quotation Digital Signature RFQ Digital Signature PO Digital Signature Odoo Digital Signature Purchases digital signature sale order Module digital sign purchase order digital sign invoice digital sign bill digital signature sales digital sign RFQ digital sign account Odoo Purchase digital sign on purchase order digital sign in purchase digital sign on purchase report purchase order digital signature on purchase digital signature on purchase order digital signature on rfq digital signature quote digital signature on quote',

    'depends': ['sale_management','account','purchase','stock'],
    'data': [
        'view/account_invoice_views.xml',
        'view/purchase_order_view.xml',
        'view/stock_picking_views.xml',
        'view/report_view.xml',
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
    
    # author and support Details =============#
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':14.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
    'qweb': ['static/src/xml/digital_sign.xml'],
    'pre_init_hook' :'pre_init_check',
}


