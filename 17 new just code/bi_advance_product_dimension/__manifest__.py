# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Advance Product Dimension and Measurement(Height-Width-Length) Odoo App',
    'version': '17.0.0.0',
    'category': 'Sales',
    'summary': 'Sale product Dimensions Manufacturing product Dimensions height and width on product height on product width on product height attribute product Width attribute Product Dimension on orders sales Product Dimension product Length product hight width Length',
    'description' :"""
        This odoo app helps user to calculate product price based dimension(M2) and based on quantity. User can configure minimum and maximum length, height, and width for product. User have option to select "Dimension Method" and enter measurement for selected product for sales order, purchase order, customer invoice, vendor bill and manufacturing order.
    """,
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.com',
    "price": 100,
    "currency": 'EUR',
    'depends': ['product','account','sale_management','stock','purchase','mrp','sale_stock','bi_product_dimension'],
    'data': [
            'views/invoice.xml',
            'views/product.xml',
            'views/sale.xml',
            'views/purchase.xml',
            'views/mrp.xml',
            'report/sale_order_report_view.xml',
            'report/purchase_order_report_templates.xml',
            'report/inherit_rfq_report.xml',
            'report/invoice_report_view.xml',
            'report/mrp_production_report_templates.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/vEyE04Pzvu8',
    "images":['static/description/Banner.gif'],
    'license': 'OPL-1',
}
