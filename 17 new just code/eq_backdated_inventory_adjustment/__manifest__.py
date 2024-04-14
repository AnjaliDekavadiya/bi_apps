# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2019 EquickERP
#
##############################################################################
{
    'name': "Inventory Adjustment Backdated",
    'category': 'Inventory',
    'version': '17.0.1.0',
    'author': 'Equick ERP',
    'description': """
        This Module allows user to do adjustments in back dated-force dated.
        * Allow user to do adjustments in back dated-force dated..
        * Update the date in stock moves and product moves.
        * Update the date in journal entries if product have automated valuation method.
    """,
    'summary': """inventory adjustment date inventory adjustment force date force date inventory adjustment back dated inventory adjustment date inventory adjustment back dated inventory force date inventory Backdate Inventory Adjustment Backdated Inventory Adjustment""",
    'depends': ['stock_account'],
    'price': 14,
    'currency': 'EUR',
    'license': 'OPL-1',
    'website': "",
    'data': [
        'views/stock_view.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
    'pre_init_hook': 'module_install_hook'
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: