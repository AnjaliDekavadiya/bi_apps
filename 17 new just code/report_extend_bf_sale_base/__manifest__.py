# -*- coding: utf-8 -*-

{
    'name': 'Report Templates Sale Base',
    'description': 'Report Templates Sale Base',
    'summary': 'Export data Odoo to LibreOffice, professional report, simple report designer, ideal for contracts, report sale order.',
    'category': 'All',
    'version': '1.0',
    'website': 'http://www.build-fish.com/',
    "license": "AGPL-3",
    'author': 'BuildFish',
    'depends': [
        'report_extend_bf',
        "sale",
        "sale_management",
    ],
    'data': [
        'views/sale_views.xml',
    ],
    'application': True,
}
