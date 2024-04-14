# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Google Maps Integration for Point of Sale',
    'version': '17.0.0.0',
    'category': 'Point of Sale',
    'summary': 'POS google map pos customer address on google map pos address on google map point of sales google map address on pos address google map pos address map on pos google map address point of sale google map address pos customer address with google map in pos',
    'description' :"""Google Maps POS Integration Odoo App brings the convenience and functionality of Google Maps directly to your point of sale system, this app simplifies address management and elevates your customer service to new heights. With this app user can search and retrieve accurate customer address information on POS, also can search and update location by drag and drop, and the customer location will automatically be updated.""",
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.com',
	'price': 25,
    'currency': 'EUR',
    'depends': ['base','web','point_of_sale'],
    'data': [
        'views/bi_pos_config_view.xml',
    ],

    'assets': {
        'point_of_sale._assets_pos': [
            "bi_pos_customer_locations_on_map/static/src/js/custMapApi.js",
            "bi_pos_customer_locations_on_map/static/src/js/BiGoogleMapApi.js",
            'bi_pos_customer_locations_on_map/static/src/xml/BiGoogleMap.xml',
        ],
     },

    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/sZMjE-xTRj8',
    "images":['static/description/Google-Maps-Integration-for-POS-Banner.gif'],
}
