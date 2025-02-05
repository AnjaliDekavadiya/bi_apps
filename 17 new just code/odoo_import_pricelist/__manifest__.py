# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Import Pricelist and Pricelist Items (Multiple)',
    'version': '8.1.1',
    'price': 49.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """Allow you to import pricelists from excel file.""",
    'description': """
Import Pricelist
This module allow you to import pricelists from excel file
import pricelist
pricelist import
pricelist item
price list import
import price list
import pricelist items
pricelist excel
excel pricelist
pricelist csv
csv pricelist
    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.png'],
    'live_test_url' : 'https://probuseappdemo.com/probuse_apps/odoo_import_pricelist/884',#'https://youtu.be/XrLp3MW2qHk',
    'category': 'Sales',
    'depends': [
                'sale',
                ],
    'data':[
        'security/ir.model.access.csv',
        'wizard/import_pricelist_wizard.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
