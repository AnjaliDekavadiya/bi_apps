{
    'name': 'Sales Advance Payments',
    'version': '17.0.1.0',
    'summary': """Advanced Payments, Advanced Down Payments or Advanced Deposits on Invoices,
Customer Invoice Advance Payments, Vendor Invoice Advance Payments,
Vendor Bill Advance Payments, Supplier Invoice Advance Payments, Odoo Advance Payments,
Odoo Advance Deposits, Sales Advance Payments, Sales Advanced Payments,
Sales Advance Down Payments, Sales Advanced Down Payments, Sales Down Payments,
Sales Advance Deposits, Sales Advanced Deposits, Sales Prepayments, Sale Advance Payments,
Sale Advanced Payments, Sale Advance Down Payments, Sale Advanced Down Payments,
Sale Down Payments, Sale Advance Deposits, Sale Advanced Deposits, Sale Prepayments,
Sales Order Advance Payments, Sales Order Advanced Payments, Sales Order Advance Down Payments,
Sales Order Advanced Down Payments, Sales Order Down Payments, Sales Order Advance Deposits,
Sales Order Advanced Deposits, Sales Order Prepayments, Sale Order Advance Payments,
Sale Order Advanced Payments, Sale Order Advance Down Payments, Sale Order Advanced Down Payments,
Sale Order Down Payments, Sale Order Advance Deposits, Sale Order Advanced Deposits,
Sale Order Prepayments""",
    'description': """
Sales Advance Payments
======================

This module adds advance payments option in sales order. Advance payments will be automatically
applied to the sales order's customer invoice once created.
""",
    'category': 'Sales/Sales',
    'author': 'MAC5',
    'contributors': ['MAC5'],
    'website': 'https://apps.odoo.com/apps/modules/browse?author=MAC5',
    'depends': [
        'account_payment_advance_mac5',
        'sale',
    ],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
    'price': 100.00,
    'currency': 'EUR',
    'support': 'mac5_odoo@outlook.com',
    'license': 'OPL-1',
    'live_test_url': 'https://youtu.be/ubbcSh2ovUE',
}
