# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Import Products using Excel",
    'version': '7.2.1',
    #'live_test_url': 'https://youtu.be/Obd7vsTXOt0',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/odoo_product_import_excel/1032',#' https://youtu.be/4_5rMIQ7FbI',
    'price': 19.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """Import your company products into Odoo using Excel.""",
    'description': """
    Odoo Product Import Excel.
    This module create product from import excel
    
    Product Import Excel
    Import Excel
    Product Excel
This module help to import product from excel.

Menus Available:
    Import product/product
products import
import products
product import
product import
product product import
products import
products import
client import
product excel import
import odoo
odoo import
import products
import product
import product
import products
vendor import
smart import
odoo import csv
odoo import excel
probuse
mustufa
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img.jpg'],
    'category' : 'Sales/Sales',
    'depends': [
                'product',
                'sale',
                'stock',
                'sale_management',
                #'stock_landed_costs',
                ],
    'data':[
            'security/ir.model.access.csv',
            'wizard/import_excel_wizard.xml',
            
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
