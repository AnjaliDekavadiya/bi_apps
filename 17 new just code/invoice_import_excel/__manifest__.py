# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Import Invoice from Excel",
    'price': 9.0,
    'version': '8.7.3',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This module will allow you to import invoice from excel.""",
    'description': """
Odoo invoice Import Excel.
Odoo invoice Import Excel
import invoice
import invoice line
invoice import
invoice line import
invoice excel import
excel import invoice
invoice import feature
odoo import
odoo import invoice
invoice line import in odoo
* INHERIT invoice.form.inherit.import.lines (form)
* INHERIT invoice.vendor.form.inherit.import.lines (form)
import.invoice.wizard (form) 
Import Invoice from Excel

This module will allow you to import invoice from excel. See video in Live Preview for more details.
Make sure you have xlwt Python module installed.

Following fields can be Import.
PRODUCT
DESCRIPTION
QUANTITY
UNIT OF MEASURE
UNIT PRICE
DISCOUNT
TAX1
TAX2
TAX3
ANALYTIC ACCOUNT
ANALYTIC TAGS
Sample is available inside module.

    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    #'live_test_url': 'https://youtu.be/Zh7TkKoPmy0',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/invoice_import_excel/768',#'https://youtu.be/MsN3bOALyks',
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.png'],
    'category' : 'Accounting/Accounting',
    'depends': [
                'account',
                ],
    'data':[
            'security/ir.model.access.csv',
            'wizard/import_excel_wizard.xml',
            'views/invoice_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
