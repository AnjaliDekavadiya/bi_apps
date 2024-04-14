# -*- coding: utf-8 -*-

{
    "name" : "Automatic Bank Synchronization | Auto Plaid Integration",
    'author': "BrowseInfo",
    "version": "17.0.0.0",
    'price': 69,
    'currency': "EUR",
    'category': 'Extra Tools',
    'website': "https://www.browseinfo.com ",
    'summary': 'Auto Bank Synchronization with Plaid Integration Online Bank Account Synchronization With Plaid Automatic Integration Bank Synchronization Via Plaid Bank Sync Connector Automatic Plaid Synchronization with Bank Sync from Plaid Sync Bank Statements Via Plaid',
    'description': """Auto Bank Synchronization module will help in bank synchronisation via plaid. It enables user to link  bank journals to their online bank accounts for supported bank institutions via plaid and configure a periodic and automatic synchronisation of their bank statements to feeds bank directly in odoo.""",
    "license": "OPL-1",
    "depends" : ['account'],
    "data": [
        "data/plaid_auto_get_transactions.xml",
        "wizard/res_config_settings.xml",
        "views/bi_plaid_bank_details_view.xml",
        "wizard/bi_plaid_transactions.xml",
        "security/ir.model.access.csv"
    ],
    'assets': {
        'web.assets_backend': [
            'https://cdn.plaid.com/link/v2/stable/link-initialize.js',
            'bi_plaid_integration/static/src/js/plaid_integration.js',
            'bi_plaid_integration/static/src/xml/plaid_integration_button.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'live_test_url': 'https://youtu.be/KqnIyiGooRo',
    "images": ['static/description/Automatic-Plaid-Synchronization-Banner.gif'],
    
}
