# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Product/Material Requisitions Stock Availibility',
    'version': '4.1.6',
    'price': 49.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category': 'Warehouse',
    'summary': """Stock on Hand show on Material Requisition""",
    'description': """
Employees/Users to create Purchase Requisitions Manage Stock Availibility
material requisition
stock on hand
on hand stock
requisition stock
product stock

    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/material_requisition_stock_availibilty/696',#'https://youtu.be/87mF8141h1Q',
    'depends': [
        'material_purchase_requisitions',
        'sale'
    ],
    'data':[
        'views/purchase_requisition_view.xml',
        'views/menu.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
