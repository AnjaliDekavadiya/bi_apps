# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Documents/Attachments on Website Shop',
    'category': 'Website',
    'license': 'Other proprietary',
    'summary': 'This module allow user to attach documents on product form which will be shown to website shop/ecommerce.',
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'https://www.probuse.com',
    'price': 79.0,
    'images': ['static/description/img1.jpg'],
    'currency': 'EUR',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/website_product_shop_attachment/704',#'https://youtu.be/SH0uXn8wGac',
    'version': '5.34.1',
    'description': """
This module allow user to attach documents on product form which will be shown to website shop/ecommerce

This module add feature on E-commerce/Eshop to allow customers to check and download product documents. For example company can allow customer to download documents like Product detail specification, Terms and condition, etc...

Customer/Portal Users/Visitors/Guest can download documents from product page on website.
 
Tags:
shop attachments
Website Product Attachments
shop documents
product attachment
website product attachment
website product shop attachment
website_product_attachment_shop
product related documents
shop product specification
odoo ecommerce documents
odoo shop documents
odoo attachments
download attachment
download from website
website page download attachment.
shop customization
eshop
shopping
website attachment
web attachment
web download
Documents on Website Shop
Attachments on Website Shop
website_product_shop_attachment


document attachment
    """,
    'depends': [
                'website_sale',
                ],
    'data': [
        'views/product_view.xml',
        'views/product_website_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
