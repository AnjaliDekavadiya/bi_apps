# -*- coding: utf-8 -*-

{
    'name': 'Report Templates Sale Order',
    'description': 'Report Templates Sale Order',
    'summary': 'Export data Odoo to LibreOffice, professional report, simple report designer, ideal for contracts, report sale order.',
    'category': 'All',
    'version': '1.0',
    'website': 'http://www.build-fish.com/',
    "license": "AGPL-3",
    'author': 'BuildFish',
    'depends': [
        'report_extend_bf',
        'report_extend_bf_sale_base',
        "sale",
        "sale_management",
    ],
    'data': [
        'data/templates.xml',
        'report.xml',
    ],
    'live_test_url': 'http://report_extend_bf.odoo15.build-fish.com',
    'price': 60.00,
    'currency': 'EUR',
    'images': ['static/description/banner.png'],
    'application': True,
}
