# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Invoices Import from Excel",
    'price': 49.0,
    'version': '7.1.11',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This app will allow you to import Invoices / Vendor Bills / Debit-Credit Notes from excel into Odoo.""",
    'description': """
Odoo invoice Import Excel
Odoo invoice Import Excel
import invoice
import invoice line
import excel
import customer invoice
import vendor bill
import invoices
invoices import
invoice import
invoice line import
invoice excel import
excel import invoice
invoice import feature
odoo import
odoo import invoice
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/odoo_invoice_import/885',#'https://youtu.be/SyUdgL41REw',
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.png'],
    'category' : 'Accounting',
    'depends': [
                'account',
                ],
    'data':[
            'security/ir.model.access.csv',
            'wizard/import_excel_wizard.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
