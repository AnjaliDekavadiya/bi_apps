# -*- coding:utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Import Sales Order Line from Excel',
    'version': '1.3',
    'price': 25.0,
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website' : 'www.probuse.com',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category': 'Sales',
    'support': 'contact@probuse.com',
    'summary':  """This module import sales order line from excel file.""",
    'description': """
Import Sales Order Line from Excel
This module import sales order line from excel file.
sale order import
sale order line import
sale import
order import
odoo import sale
sales order import
sales order lines import
import sales line
import sales order line
sales order import
sales line import
sales order line import
sales order line excel import
import sales order excel
import sale order excel
import sales order data
import excel sales order line
import excel sales order
import so
import so lines
import order from excel
import order from xls
sales quotation import
sale line import
sale import excel
    """,
    'images': ['static/description/import.jpg'],
    'live_test_url': 'https://youtu.be/wF8sYlIf4Qg',
    'external_dependencies': {'python': ['xlrd']},
    'depends': ['sale'],
    'data': [
        'wizard/sale_order_line_import_view.xml',
        'views/sale_views.xml',
    ],
    'installable' : True,
    'application' : True,
    'auto_install' : False,
}
