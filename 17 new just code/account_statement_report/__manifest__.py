# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

{
    'name': 'Account Statement Report',
    'version': '17.0.1.0',
    'license': 'OPL-1',
    'category': 'Accounting/Accounting',
    'author': 'Kanak Infosystems LLP.',
    'website': 'https://kanakinfosystems.com',
    'summary': '''
Print Account statement Report in PDF and XLS Format, user can print individual or all account statements and apply filters.
Account Statement
Account Report
PDF Report
XLS Report
Accounting
Individual Report
Chart Of Accounts''',
    'description': '''
This module contain Account Statement Report in pdf and xls format.
    ''',
    'depends': [
        'account'
    ],
    'data': [
        'security/ir.model.access.csv',
        'report/report_qweb.xml',
        'report/report_view.xml',
        'wizard/account_statement_wizard.xml',
    ],
    'images': [
        'static/description/account_statement_report_banner.png'
    ],
    'installable': True,
    'price': 30,
    'currency': 'EUR',
    'live_test_url': 'https://youtu.be/xgnuTSCuj4c',
}
