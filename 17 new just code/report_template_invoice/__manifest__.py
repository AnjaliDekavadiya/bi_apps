# -*- coding: utf-8 -*-

{
    'name': 'Customized Invoice Designs',
    'version': '1.0',
    'summary': """Configurable Customized Invoice Templates. Professional /  donwload print reporting / Colourful  and Flexible / Header Footer / Amount in Words / Signature / Watermark / Logo / Font Size Style Family / Arabic / Product Image / colorful / clever custom invoices""",
    'description': """Configurable Customized Invoice Templates""",
    'category': 'Accounting/Accounting',
    'author': 'bisolv',
    'website': "www.bisolv.com",
    'license': 'AGPL-3',

    'price': 120.0,
    'currency': 'USD',

    'depends': ['base', 'account',
                'report_utils'
                ],

    'data': [
        'report/paperformat.xml',
        'report/template1.xml',
        'report/report.xml',
        'views/config_view.xml',
    ],
    'demo': [

    ],
    'images': ['static/description/banner.png'],
    'qweb': [],

    'installable': True,
    'auto_install': False,
    'application': False,
}
