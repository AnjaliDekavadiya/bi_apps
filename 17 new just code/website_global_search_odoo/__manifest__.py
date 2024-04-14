# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Global Search Product On Website Pages",
    'price': 49.0,
    'currency': 'EUR',
    'category' : 'Website',
    'license': 'Other proprietary',
    'summary' : 'This app allow your customers to do global search on Product and Product Category Filter in all website pages.',
    'description': """
website search
search web
search product
product search
product category search
global search
website_search
Website search
Website Search Suggestion
Global Product Search on website
Product Global Search
Search over pages
Advanced search
Advance search
shop search
Website Searchbox
ecommerce search

    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/website_global_search_odoo/845',#'https://youtu.be/s-8ARzEpf4E',
    'version': '6.1.5',
    'depends': [
        'website',
        'website_sale'
    ],
    'data':[
        'views/website_search_box.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            '/website_global_search_odoo/static/src/js/product_category_display.js',
        ],
    },
    'installable' : True,
    'application' : False,
    'auto_install' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
