# -*- coding: utf-8 -*-

{
    'name': 'Professional Template Purchase Base',
    'description': 'Professional Template Purchase Base',
    'summary': 'Export data Odoo to LibreOffice.',
    'category': 'All',
    'version': '1.0',
    'website': 'http://www.build-fish.com/',
    "license": "AGPL-3",
    'author': 'BuildFish',
    'depends': [
        'report_extend_bf',
        'purchase',
    ],
    'data': [
        'views/purchase_views.xml',
    ],
    'application': True,
}
