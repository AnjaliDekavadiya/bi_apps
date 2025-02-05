# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Purchase Order Import (Multiple Purchase Order Import)',
    'version': '9.1.2',
    'price': 19.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This app allow you to import multiple purchase order from excel file.""",
    'description': """
Odoo Multiple purchase order Import.
This module import purchase entries from excel file
purchase order Import from Excel
Import purchase order
Import purchases
Import purchase
purchase order import
import purchase
import purchase order odoo
import purchase order
purchase order import
purchase import
purchase entries import
import purchase entries
opening entry import
opening balance import
partner balance import
purchase order excel import
purchase order excel import

    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.png'],
    # 'live_test_url' : 'https://probuseappdemo.com/probuse_apps/odoo_purchase_order_import/994',#'https://youtu.be/21MgsP8jPfg',
    'category': 'Purchases',
    'depends': [
                'purchase',
                ],
    'data':[
        'security/ir.model.access.csv',
        'wizard/purchase_order_wizard_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
