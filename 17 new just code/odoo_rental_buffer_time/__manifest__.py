# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Buffer Time in Product Rental",
    'summary': """Rental Product and Buffer Time""",
    'description': """
    
rental app
app rental
odoo rental
rental buffer time
buffer time rental
rent
product rent
rental items
odoo rent apo
odoo rental app

    """,
    'currency': 'EUR',
    'price': 99.0,
    'version': '7.1.1',
    'license': 'Other proprietary',
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    #'live_test_url':'https://youtu.be/tcDJHedAD0w',
    'category' : 'Website/Sale',
    'depends': [
        'odoo_rental_request_management',
    ],
    'data':[
        'security/ir.model.access.csv',
        'views/product_view.xml',
        'views/rental_buffer_time_views.xml',
        'views/sale_order_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
