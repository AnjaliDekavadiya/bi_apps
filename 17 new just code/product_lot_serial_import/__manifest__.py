# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.
{
    'name': "Product Lot Serial Import from Excel",
    'price': 9.0,
    'currency': 'EUR',
    'category': 'Inventory/Inventory',
    'license': 'Other proprietary',
    'summary' : 'Product Lot Serial Import from Excel',
    'description': """
Product Lot Serial Import from Excel
odoo lot import
lot import
lot serial number import
serial number import
import lot number
import serial number
import product lot
import product serial number
   """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    #'live_test_url': 'https://youtu.be/1arSjwLxDvY',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/product_lot_serial_import/861',#'https://youtu.be/1umEByU_5lE',
    'images': ['static/description/img1.png'],
    'version': '6.1.2',
    'depends': ['stock','product_expiry'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/lot_import_wizard_view.xml',
    ],
    'installable' : True,
    'application' : False,
    'auto_install' : False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
