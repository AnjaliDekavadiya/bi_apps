# -*- coding: utf-8 -*-

{
    'name' : 'All in One Receipt Reports - Sales, Purchase, Accounting, Inventory',
    'author': "Edge Technologies",
    'version' : '1.0',
    'live_test_url':'https://youtu.be/dr8n-Hf3z6A',
    'images':['static/description/main_screenshot.png'],
    'summary' : 'Print all receipt report for sales receipt report for purchase receipt report for invoices receipt report for inventory receipt report for all in one report for print sales receipt print purchase receipt print invoice receipt print sale order receipt',
    'description' : """
        This module is useful for print odoo standard reports in receipt printer.
    """,
    "license" : "OPL-1",
    'depends' : ['sale_management','purchase','account','stock'],
    'data': ['report/sale_receipt_report.xml','report/sale_receipt_template.xml',
            'report/purchase_receipt_report.xml','report/purchase_receipt_template.xml',
            'report/delivery_receipt_report.xml','report/delivery_receipt_template.xml',
            'report/invoice_receipt_report.xml','report/invoice_receipt_template.xml',
            'report/payment_receipt_report.xml','report/payment_receipt_template.xml'],
    'qweb' : [],
    'demo' : [],
    'installable' : True,
    'auto_install' : False,
    'price': 28,
    'currency': "EUR",
    'category' : 'Sales',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
