# -*- coding: utf-8 -*-
{
    'name': "Disable Right Click for Product Page of Shop",
    'version': '6.1.2',
    'price': 9.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category': 'Website/Website',
    'summary': """Block Right Click on Product Image of Product Page of Ecommerce in Odoo""",
    'description': """
Disable Right Click for Product Page of Shop
    """,

    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': 'www.probuse.com',
    'images': ['static/description/image.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/disable_right_click_website_product/714',#'https://youtu.be/BPQeB96RdBc',
    'depends': ['website_sale'],

    'data': [
        # 'views/views.xml',
    ],
    'assets': {
        'web.assets_frontend': 
        [
            'disable_right_click_website_product/static/src/js/right_click_disable.js',
        ],
    },
    'installable': True,
    'application': False,
}
