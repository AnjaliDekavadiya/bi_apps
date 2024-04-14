# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Import Chart of Accounts using Excel",
    'license': 'Other proprietary',
    'currency': 'EUR',
    'price': 9.0,
    'summary': """Import your company chart of accounts into Odoo using Excel.""",
    'description': """
This module help to import customer from excel.
csv import account
account import
import account excel
import chart of account
chart of accounts import
import coa
coa import
import account chart of account
account chart import
import all account
accounting import
external account
csv import account
excel import account
Import Chart of Accounts using Excel
Import your company chart of accounts into Odoo using Excel.
Make sure you have xlwt Python libarary installed.
Menus Available:
Import Chart of Account
account
chart of account
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
   # 'live_test_url': 'https://youtu.be/aKRL_TqFmBo',
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/2.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/odoo_chart_account_import/743',#'https://youtu.be/JpOgxUVhNU4',
    'version': '8.6.1',
    'category' : 'Sales/Sales',
    'depends': [
                'account',
                ],
    'data':[
        'security/ir.model.access.csv',
        'wizard/import_account_xls_view.xml',
        'views/import_chart_of_account_menu.xml',
    ],
    'installable' : True,
    'application' : False,
    'auto_install' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
