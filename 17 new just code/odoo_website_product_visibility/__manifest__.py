# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Website Product Visibility for Customer and Guest Users',
    'version': '9.1.4',
    'price': 49.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category': 'Website/Website',
    'summary': 'This module allow you to have visibility of your products and category on website shop for guest and logged user.',
    'description': """
Odoo Website Product Visibility
This module allow limited product show by customer and public user on website
website_product_visibility
website_sale_category_visibility
Product Category Visibility
Product Visibility
Product template Visibility
Website Product Visibility for Log in users and Visitors
Website Product Visibility for Customer and Guest
filter Products
filter Product category
product visibility based on customer on webshop
Product visible in webshop
Product visible in shop
Product visible in ecommerce
Customer Website View
Configure Visitor Product
Odoo Website Product Visibility
Configure Visitor Products
ecommerce
eshop
Public Guest Visibility
product guest visibility
website shop
shop
odoo shop
product restriction
product show
product hide
product visiblity
Website Product Visibility
Website Product
Website Product category
category website
product on website shop
Product visibility in e-commerce
e-commerce Product visibility
products on website
product on website
product on shop

    """,
    'images': ['static/description/image.png'],
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    # 'live_test_url': 'https://youtu.be/b_CKB6WUsqs', #'https://youtu.be/ao1cegGpI8c',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/odoo_website_product_visibility/128',#'https://youtu.be/TF7Pg3jxtHU',
    'depends': [
        'website_sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_view.xml',
        'views/public_shop_visibility_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
