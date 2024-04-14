# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

{
    'name': 'Website Signup on Checkout Page',
    'version': '17.0.1.0',
    'license': 'OPL-1',
    'category': 'Website/Website',
    'author': 'Kanak Infosystems LLP.',
    'website': 'https://kanakinfosystems.com',
    "summary": '''
        This module allows the user to signup on the checkout page and makes the user checkout experience faster by limiting the no. of steps user has to go through in a default Odoo environment.
        website signup | user signup | Portal access | checkout sinup | User create | User creation on checkout
    ''',
    'description': '''
        This module allows toSignup on Checkout page.
    ''',
    'depends': [
        'website_sale'
    ],
    'data': [
        'data/knk_auth_signup_data.xml',
        'views/knk_website_sale_templates.xml',
        'views/knk_res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_checkout_signup_knk/static/src/js/knk_webiste_sale.js',
        ],
    },
    'post_init_hook': '_auto_website_signup_b2c',
    'images': ['static/description/banner.jpg'],
    'installable': True,
    'price': 55,
    'currency': 'EUR',
}
