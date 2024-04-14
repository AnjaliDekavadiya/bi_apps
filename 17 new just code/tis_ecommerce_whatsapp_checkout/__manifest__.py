# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2022. All rights reserved.

{
    'name': 'eCommerce WhatsApp Checkout',
    'version': '17.0.0.0',
    'summary': 'eCommerce WhatsApp Checkout',
    'sequence': 1,
    'author': 'Technaureus Info Solutions Pvt.Ltd.',
    'description': 'This module is for eCommerce WhatsApp Checkout',
    'category': 'eCommerce',
    'website': 'http://www.technaureus.com',
    'depends': ['website_sale'],
    'license': 'Other proprietary',
    'price': 35,
    'currency': 'EUR',
    'data': [
        'views/templates.xml',
        'views/res_config_settings_views.xml',
        'views/website.xml',
    ],
    'images': ['images/main_screenshot.png'],
    'assets': {
        'web.assets_frontend': [
            'tis_ecommerce_whatsapp_checkout/static/src/js/website_clear_cart.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
