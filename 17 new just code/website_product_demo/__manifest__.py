# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Request Demo Website Shop/Ecommerce',
    'category': 'Website/Website',
    'license': 'Other proprietary',
    'summary': 'Request Demo Website Shop/Ecommerce',
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'https://www.probuse.com',
    'price': 20.0,
    'currency': 'EUR',
    'version': '8.2.4',
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    # 'live_test_url': 'https://youtu.be/GZsjPN4VJs8',
    'live_test_url' : 'https://probuseappdemo.com/probuse_apps/website_product_demo/351',#'https://youtu.be/F9-wuRMXijI',
    'description': """
Request Demo Website Shop/Ecommerce

This module allow user to send request for product demo through website shop/ecommerce.
Customer can request demo from website shop and that will create lead in Odoo backend.
This app will work for logged in customer and also work for your visitor of your website.
    This module allow user to send request for product demo through website.
Request Demo Website Shop/Ecommerce
Demo for Product
Request for demo
Product Demo
Website demo
request demo
request for demo
eshop demo
shop demo
website_sale demo
product demo
demo request
demo user
customer demo
customer demo request
visitor demo request
demo video
demo to user
website shop
wevsite ecommerce
e-commerce demo
website quote demo
     """,
    'depends': ['product','website_sale','crm'],
    'data': [
        # 'views/template.xml',
        'views/product_website_view.xml',
        'datas/mail_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_product_demo/static/src/js/website_sale.js',
        ],
    },
    'installable': True,
    'auto_install': False,
}
