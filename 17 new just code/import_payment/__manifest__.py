# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.
{
    'name': "Import Customer/Supplier Payments - Excel",
    'price': 29.0,
    'version': '6.1.5',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This module will account department to import customer and supplier Payments data from .xls or .xlsx files.""",
    'description': """
        Import Payment From .xls or .xlsx

Import Customer/Supplier Payments From Excel

This module will account department to import customer and supplier Payments data from .xls or .xlsx files.

You have to install xlrd python package on your server/machine/instance to use this app.

Menu: Invoicing/Import/Import Payments 

You can only import fields shown on excel sample. 

Import Excel Format Available in Doc Folder inside module.

Tags:
Payments Import .xls
Supplier Payment Import
Customer Payment Import
Import Payments
import payment
import customer payment
import supplier payment
import payments in odoo
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "www.probuse.com",
    'support': 'contact@probuse.com',
    'category': 'Accounting/Accounting',
    'depends': ['account'],
    'images': ['static/description/1.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/import_payment/969',#'https://youtu.be/M9W6O-5QRW8',
    'data':[
        'security/ir.model.access.csv',
        'views/res_partner_view.xml',
        'wizard/import_payment_view.xml',
    ],
    'installable' : True,
    'application' : True,
    'auto_install' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
