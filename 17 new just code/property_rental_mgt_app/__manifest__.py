# -*- coding : utf-8 -*-

{
    'name' : 'Property Sale, Lease and Rental Management App',
    'author': "Edge Technologies",
    'version' : '17.0.1.0',
    'live_test_url':'https://youtu.be/qp0V-bN-Poo',
    "images":['static/description/main_screenshot.png'],
    'summary' : 'Apps for sale property management rent property management real estate property management real estate lease management property lease management property booking property rental property rental invoice housing rental housing lease house rental',
    'description': "Sale & Rent property management ,create contract, renew contract, allow partial payment for sale property and invoice due date auto generate between one month interval, maintain property maintenance, user commission calculate at register payment time base on property, automatically generate commission worksheet at last of day of the month. view and print contract expired report, property analysis report.",
    'depends': ['product','sale','account', 'stock'],
    "license" : "OPL-1",
    'data': [
        'security/ir_module_category_data.xml',
        'security/ir.model.access.csv',
        'views/configuration.xml',
        'views/maintanance.xml',
        'views/property_purchase.xml',
        'views/property_reserve.xml',
        'views/contract_details.xml',
        'views/renew_contract.xml',
        'views/commission.xml',
        'views/property_product.xml',
        'views/property_partners.xml',
        'views/property_offer.xml',
        'views/property_search.xml',
        'views/property_menu.xml',
        'report/contract_template.xml',
        'views/res_config_setting.xml',
        'data/ir_sequence_data.xml',
        'data/property_reminder.xml',
        'data/property_mail_template.xml',

    ],

    'qweb' : ['static/src/xml/*.xml'],
    'demo' : [],
    'installable' : True,
    'auto_install' : False,
    'price': 79,
    'currency': "EUR",
    'category' : 'Sales',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
