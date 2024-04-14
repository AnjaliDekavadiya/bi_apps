# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Sale/Purchase Inventory Tags",
    'price': 99.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This module add inventory tags on sale order and purchase order and pass inventory tags on Delivery.""",
    'description': """
        This module add inventory tags on sale and purchase order and pass inventory tags on Delivery.
     
     Inventory Tags
     Inventory Tag
     Tags for Inventory
  sales tag
    purchase tag
    sale tags
    purchase tags
    inventory tags on sales order
    inventory tags on purchase order
    inventory tags on sale order
    tagging
    sales tagging
    stock tags
    warehouse tags
    stock warehouse tags

    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/sale_purchase_inventory_tags/893',#'https://youtu.be/Pr_jU5So7bM',
    # 'version': '4.1.2.4',
    'version': '5.1.2',

    'category' : 'Warehouse',
    'depends': ['sale','purchase','stock','sale_purchase'],
    'data':[
        'security/ir.model.access.csv',
        'views/inventory_tags.xml',
        'views/sale_view.xml',
        'views/purchase_view.xml',
        'views/stock_view.xml',
    ],
    'installable' : True,
    'application' : False,
    'auto_install' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
