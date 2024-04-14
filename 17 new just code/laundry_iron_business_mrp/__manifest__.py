# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Laundry Services Request with Manufacturing Orders",
    'version': '4.2.3',
    'license': 'Other proprietary',
    'currency': 'EUR',
    'price': 49.0,
    'summary': """Laundry Services / Dry Cleaning Services Request with Manufacturing Order / Work Orders of MRP.""",
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img12.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/laundry_iron_business_mrp/476',#'https://youtu.be/aygeBQH7iO8 ',
    'category' : 'Manufacturing/Manufacturing',
    'depends': [
        'mrp',
        'laundry_iron_business',
                ],
    'description': """
        This app allows you to create manufacturing orders / work orders of MRP from laundry requests as shown in below screenshots.
Laundry Services Request with Manufacturing Orders

    """,
    'data':[
        'security/ir.model.access.csv',
        'views/laundry_service_support_view.xml',
        'views/mrp_production_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
