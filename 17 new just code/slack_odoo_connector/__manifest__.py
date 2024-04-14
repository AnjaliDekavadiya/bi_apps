# -*- coding: utf-8 -*-
{
    'name': "Slack Odoo Connector",

    'summary': """Slack Odoo Integration""",

    'description': """Odoo is a fully integrated suite of business modules that encompass the traditional ERP functionality. Odoo Slack allows you to send updates on your Slack.
    """,

    'author': "Techloyce",
    'website': "http://www.techloyce.com",


    'category': 'sale',
    'version': '17.1.0',
    'price': 349,
    'currency': 'EUR',
    "license": "OPL-1",


    # any module necessary for this one to work correctly
    'depends': ['mail','base'],
    'images': [
        'static/description/banner.gif',
    ],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/slack_settings.xml',
        'views/templates.xml',
        'views/res_user.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'external_dependencies': {'python': ['slack', 'slackclient']},
}
