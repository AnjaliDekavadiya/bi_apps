# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Ask Question on Website Product Page',
    'version' : '5.1.4',
    'price' : 29.0,
    'currency': 'EUR',
    'category': 'Website/Website',
    'license': 'Other proprietary',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/website_product_ask_question/1247',#'https://youtu.be/TT4plPy3NTc',
    'images': [
        'static/description/ask_image.png',
    ],
    'description': """
This app allows your customer and guest of a website to ask questions about a product from ecommerce.
Website Product Ask Question
    """,
    'summary' : 'Your customer can ask question about a product from ecommerce.',
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website' : 'wwww.probuse.com',
    'depends' : [
        'website_sale',
        'crm'
    ],
    'support': 'contact@probuse.com',
    'data' : [
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_product_ask_question/static/src/js/website_sale.js',
        ],
    },
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
