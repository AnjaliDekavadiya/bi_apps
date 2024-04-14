# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.
{
    'name': "Show Product Internal Reference on POS",
    'price': 13.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This module Show Product Internal Reference on POS Screen and Receipt.""",
    'description': """
Show Product Internal Reference on POS
Show the default code of product on pos product screen and payment receipt
This module Show Product Internal Reference on POS Screen and Receipt.
pos code
pos default code 
pos internal reference
point of sale
point of sales code
point of sale code
point of sale internal reference
pos product code
pos product reference code
default code
""",
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/1ps.png'],
    # 'live_test_url': 'https://youtu.be/NbxocFZerGA',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/pos_product_code/625',#'https://youtu.be/h14ul0_C2xU',
    'version': '7.2',
    'category' : 'Sales/Point of Sale',
    'depends': ['point_of_sale'],
    'data':[
    ],
    'assets': {
#        'web.assets_qweb': [
        # 'point_of_sale.assets': [
        'point_of_sale.assets_prod':[
            'pos_product_code/static/src/js/product_card.js',
            'pos_product_code/static/src/xml/pos.xml',
            'pos_product_code/static/src/xml/product_card.xml',
        ],
    },
#    'qweb' : [
#        'static/src/xml/pos.xml',
#    ],
    'installable' : True,
    'application' : False,
    'auto_install' : False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
