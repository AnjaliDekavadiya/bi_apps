# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

{
    'name': 'Cheque Format',
    'version': '17.0.1.0',
    'license': 'OPL-1',
    'category': 'Accounting/Accounting',
    'author': 'Kanak Infosystems LLP.',
    'website': 'https://kanakinfosystems.com',
    'summary': '''
        Design your own bank cheque formats using this module and be able to print cheques from the Odoo system. | Accounting | Banking | Cheque | Custom Cheque | Cheque format | Cheque Print | Odoo Custom Format | Payment Cheque
    ''',
    'description': '''
        Configure the cheque format from menu 'Invoicing -> Configuration -> Cheque Format'
        Select cheque format in account payment record
        Now able to print the the report 'Print Cheque'
    ''',
    'depends': [
        'account'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/payment_cheque_format.xml',
        'views/cheque_format_view.xml',
        'report/print_cheque.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'installable': True,
    'currency': 'EUR',
    'price': 30
}
