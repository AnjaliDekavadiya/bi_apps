# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.
{
    'name': "Import Employees from Excel",
    'version': '6.2',
    'price': 29.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This module allow you to import Employees from excel.""",
    'description': """
This module help to import Employee from excel.
In this module for import Employee you should create .xls or .xlsx,
import employee
import employees
import hr employee
employee import
employee import excel
employee import csv
employees import
Import Employees from Excel
""",
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/odoo_import_employee_excel/879',#'https://youtu.be/aGdDcL1PLKA',
    'category' : 'Human Resources',
    'depends': [
        'hr',
    ],
    'data':[
        'security/ir.model.access.csv',
        'wizard/import_employee_excel_wizard_view.xml',
        'views/menu.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
