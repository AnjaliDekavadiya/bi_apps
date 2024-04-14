# -*- coding: utf-8 -*-
#################################################################################
# Author      : Terabits Technolab (<www.terabits.xyz>)
# Copyright(c): 2021-23
# All Rights Reserved.
#
# This module is copyright property of the author mentioned above.
# You can't redistribute/reshare/recreate it for any purpose.
#
#################################################################################
{
    'name': 'Simplify Import Export',
    'version': '17.0.2.0.0',
    'summary': """ Our access management export and import features make it easier to move access rules from staging to production environments. Second benefit, now you can save the configured access rules by exporting and using them for backup purposes, which you can then import back into the same instance if needed. """,
    'sequence': 10,
    'author': 'Terabits Technolab',
    'license': 'OPL-1',
    'website': 'https://www.terabits.xyz',
    'description': """ Our access management export and import features make it easier to move access rules from staging to production environments. Second benefit, now you can save the configured access rules by exporting and using them for backup purposes, which you can then import back into the same instance if needed. """,
    'depends': ['simplify_access_management'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/import_document.xml',
        'data/action.xml',
        'views/view_access_management.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '/simplify_import_export_bits/static/src/js/sam_list_view.js',
            '/simplify_import_export_bits/static/src/xml/sam_list_view.xml',
        ]
    },
    "price": "99.99",
    "currency": "USD",
    'live_test_url': 'https://www.terabits.xyz/request_demo?source=index&version=16&app=simplify_access_management',
    'images': ['static/description/banner.png'],
    'application': True,
    'installable': True,
    'auto_install': False,

}
