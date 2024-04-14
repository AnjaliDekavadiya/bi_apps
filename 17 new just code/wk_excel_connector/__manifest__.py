# -*- coding: utf-8 -*-
##########################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
##########################################################################

{
    'name': 'Excel Odoo Connector',
    'version': '6.0.0',
    'category': 'Generic Modules',
    'author': 'Webkul Software Pvt. Ltd.',
    'website': 'https://store.webkul.com/odoo-excel-connector.html',
    'sequence': 1,
    'summary': 'Odoo Excel Connector integrates your Odoo to Excel. It allows syncing data from Odoo to Excel or LibreOffice.',
    "license":  "Other proprietary",
    'live_test_url': 'https://odoodemo.webkul.com/?module=wk_excel_connector',
    'description': """
Excel Odoo Connector
====================
This Brilliant Module will Connect Odoo with MS Excel and Synchronise Data.
---------------------------------------------------------------------------
excel odoo connector
odoo excel connector
    """,
    'depends': [
        'mail'
    ],
    'data': [
        'views/excel_template.xml',
        'views/menu.xml',
        'security/security.xml',
        'security/ir.model.access.csv'
    ],
    "images" : ['static/description/banner.png'],
    'application': True,
    'installable': True,
    'auto_install': False,
    'currency': 'USD',
    'price': 99,
    'pre_init_hook': 'pre_init_check'
}
