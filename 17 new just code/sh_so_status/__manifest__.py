# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

{
    'name': 'Sale Order Status',
    'author': 'Softhealer Technologies',
    'website': 'https://www.softhealer.com',
    'support': 'support@softhealer.com',
    'category': 'Sales',
    'license': 'OPL-1',
    'summary': 'Sale Order Delivery Module, Filter Sale Order Invoice,SO Partial Delivery App, Find Full Paid Amount In SO Application, Partial SO Paid Amount Status Sale Order Delivery and Invoicing Status Odoo',
    'description': """This module useful to get status of delivery and invoices of sale orders. Easily filters sale orders with delivered, partial delivered, paid, partially paid.Sale Order Delivery And Invoice Status Odoo,Status Of Sale Order Delivery Module, Filter Sale Order Partial Invoice, Status Of Partial Delivery, Find Full Delivery In SO, Status Of Full Paid Amount Odoo.
  Sale Order Delivery Module, Filter Sale Order Invoice,SO Partial Delivery App, Find Full Paid Amount In SO Application, Partial SO Paid Amount Status Odoo.""",
    'version': '0.0.1',
    'depends': ['sale_management', "stock", ],
    'application': True,
    'data': [
        'views/sale_views.xml',
        'report/sale_report.xml',
        'report/invoice_report.xml',
        'report/stock_report.xml',
    ],
    'images': ['static/description/background.jpg'],
    'live_test_url': 'https://youtu.be/X_eOGGJWrfY',
    'auto_install': False,
    'installable': True,
    'price': 13,
    'currency': 'EUR',
}
