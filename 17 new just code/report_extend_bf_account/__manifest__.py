# -*- coding: utf-8 -*-

{
    'name': 'Professional Template Account Invoice',
    'description': 'Professional Template Account Invoice',
    'summary': 'Export data Odoo to LibreOffice, professional report, simple report designer, ideal for contracts, report account invoice.',
    'category': 'All',
    'version': '1.0',
    'website': 'http://www.build-fish.com/',
    "license": "AGPL-3",
    'author': 'BuildFish',
    'depends': [
        'report_extend_bf',
        'account',
        'report_extend_bf_account_base'
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
