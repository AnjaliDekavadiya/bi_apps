# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. 
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Hide Price on Shop Ecommerce of Products',
    'version': '8.1.2',
    'price': 149.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category' : 'Website/Website',
    'summary': """Hide Product Prices on Ecommerce Shop Website""",
    'description': """
Hide Price on Ecommerce Website
Hide Price on Shop Ecommerce of Products
Hide Product Prices on Ecommerce Shop Website
Hide Price from website shop product kanban box
Hide shoping cart button from product kanban box.
Hide Price from website shop product list
Hide Shoping cart button from product list
Hide price and shopping cart button form Website product page
Hide Price and Shoping cart button from whishlist product list
Hide Price and Shoping cart button from compare product list
Hide Price from recently viewed product list
Hide Price from search input box dropdown list
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/hide_price_ecommerce_website/296',#'https://youtu.be/yesj5EpQPBI',
    'depends': [
        'website_sale',
        'website_sale_wishlist',
        'website_sale_comparison',
    ],
    'data':[
        'security/hide_price_web_shop_security.xml',
        'views/website_show_view.xml',
        # 'views/templates.xml',
        'views/templates_new.xml',
        'views/whish_list_template_view.xml',
        'views/comparison_template_view.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'hide_price_ecommerce_website/static/src/js/website_sale_recently_viewed.js',
        ],
    },
    'qweb': ['static/src/xml/website_sale_recently_viewed.xml'],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

