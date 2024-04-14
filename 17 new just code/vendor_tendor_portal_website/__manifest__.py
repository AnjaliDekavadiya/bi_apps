# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. 
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Purchase Tendor Vendor Portal',
    'version': '8.1.2',
    'price': 29.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category' : 'Operations/Purchase',
    'summary': """Purchase tendor website vendor portal app.""",
    'description': """
Vendor Tendor Website Portal
Vendor Agreements Portal
Vendor Tendor's Purchase Order
Purchase Tendor Vendor Portal
purchase vendor portal
purchase tendor
tendor
odoo tendor management portal
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/vendor_tendor_portal_website/299',#'https://youtu.be/QR_zu5ipJq0',
    'depends': [
        'purchase',
        'purchase_requisition',
        'portal',
    ],
    'data':[
        'views/vendor_bid_template_views.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

