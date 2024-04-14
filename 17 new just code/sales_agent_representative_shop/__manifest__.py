# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. 
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Commission Sales Agent Select on Website Shop',
    'version': '7.1.3',
    'price': 199.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category' : 'Sales/Sales',
    'summary': """Commission Sales Agent Select on Website Shop""",
    'description': """
Sales Agent Represntative Shop
Sales Commission Agent Represntative Shop
sales commission
commission
sales agent on website ecommerce
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/sales_agent_representative_shop/297',#'https://youtu.be/oXiGbAJbYzw',
    'depends': [
        'sales_commission_external_user',
        'payment',
        'website_sale'
    ],
    'data':[
        'views/res_partner_view.xml',
        'views/payment_templates.xml',
        'views/sales_commission_level_views.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

