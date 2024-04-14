# -*- coding: utf-8 -*-
{
    'name': 'Follow Website Shop Product',
    'version': '4.1.3',
    'price': 39.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category' : 'Website/Website',
    'summary': """Customer Follow Website Shop Product""",
    'description': """
Follow Website Shop Products
follow product
product follow
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/image.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/follow_website_shop_products/807',#'https://youtu.be/y7fQQuysOqM',
    'depends': ['website_sale'],
    'assets': {
        'web.assets_frontend': [
            '/follow_website_shop_products/static/src/js/follow_unfollow.js',
        ],
    },
    'data': [
        'security/ir.model.access.csv',
        'data/product_follow_mail.xml',
        'wizard/product_history_wizard_view.xml',
        'views/follow_product_history_view.xml',
        'views/website_templates.xml',
    ],
    'installable' : True,
    'application' : False,
}
