# -*- coding: utf-8 -*-

{
    'name': 'Account Reccuring Payment App',
    "author": "Edge Technologies",
    'version': '17.0.1.0',
    'live_test_url': "https://youtu.be/H1E04B5ts_A",
    "images":['static/description/main_screenshot.png'], 
    'summary': 'Recurring Invoice Payment Recurring Account Recurring Payment invoice Recurring payment in accounting Recurring payment subscription recurring subscription payment account subscription payment in account payment recurring payment option in account',
    'description': 'Account Reccuring Payment App',
    'license': "OPL-1",
    'depends': ['base' ,'account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/reccuring_payments_views.xml',
        'views/reccuring_templates_views.xml',
        'views/reccuring_payment.xml',
    ],
    'installable': True,
    'auto_install': False,
    'price': 20,
    'currency': "EUR",
    'category': 'Accounting',
}