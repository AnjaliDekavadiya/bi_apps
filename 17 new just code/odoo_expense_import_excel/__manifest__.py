# -*- coding:utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Import Expense and Expense Sheet from Excel',
    'version': '5.1.16',
    'category': 'Human Resources',
    'license': 'Other proprietary',
    'price': 15.0,
    'currency': 'EUR',
    'summary':  """Allow you to import Expenses and Expense Sheet from excel file.""",
    'description': """
Import Expense and Expense Sheet from Excel
This module allow you to Import Expense and Expense Sheet from excel file.
import expense
import expense line
import expenses
import expense lines
import expense sheet
import expense sheets
excel expense import
import execl import
csv expense
expense sheet import
expense import
expense line import
expenses import
    """,
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website' : 'www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/image.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/odoo_expense_import_excel/780',#'https://youtu.be/S-RbsBYykZc',
    'external_dependencies': {'python': ['xlrd']},
    'depends': ['hr_expense'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/multipal_expense_import_wizard_view.xml',
    ],
    'installable' : True,
    'application' : False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: 
