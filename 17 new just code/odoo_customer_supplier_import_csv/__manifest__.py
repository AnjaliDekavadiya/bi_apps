# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Import Customers and Suppliers Excel',
    'license': 'Other proprietary',
    'price': 9.0,
    'currency': 'EUR',
    'summary': """Import your customers and suppliers into Odoo using Excel.""",
    'description': """
This module help to import customer from excel.
Menus Available:
    Import Customer/Supplier

customer import
supplier import
customer supplier import
customers import
suppliers import
client import
customer excel import
import odoo
odoo import
import customers
import customer
import supplier
import suppliers
vendor import
smart import
odoo import csv
odoo import excel

    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/cci.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/odoo_customer_supplier_import_csv/1014',#'https://youtu.be/vxo5wcJhkLE',
    'version': '6.1.5',
    'category' : 'Sales/Sales',
    'depends': [
                'base',
                'sale',
                'sale_management',
                ],
    'data':[
        'security/ir.model.access.csv',
        'wizard/import_customer_xls_view.xml',
        'views/import_customer_menu.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
