# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.
{
    'name': "Import Analytic Accounts from Excel",
    'currency': 'EUR',
    'price': 9.0,
    'license': 'Other proprietary',
    'category': 'Account',
    'summary': """This app allow import Analytic Accounts from selected excel file on wizard.""",
    'description': """
import analytic account
import analytic accounts
analytic account import
Import Analytic Accounts from Excel
    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'support': 'contact@probuse.com',
    # 'live_test_url': 'https://youtu.be/NY825hfQaLU',
    # 'live_test_url' : 'https://probuseappdemo.com/probuse_apps/import_analytic_account/187',#'https://youtu.be/JhmhXYxbqnE ',
    # 'images': ['static/description/a1.png'],
    'images':['static/description/img.jpg'],
    'version': '6.26',
    'depends': ['base','account'],
    'external_dependencies': {'python': ['xlrd']},
    'data': [
       'security/ir.model.access.csv',
       'wizard/analytic_account_import_view.xml',
    ],
    'installable': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
