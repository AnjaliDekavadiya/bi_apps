# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Send by Email Ecommerce Shop and Portal',
    # 'version': '4.1.3.3',
    'version': '4.1.3',
    'price': 9.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """Allow your customers to receive order by Email in shop and portal.""",
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'images': ['static/description/wse.png'],
    #'live_test_url' : 'https://youtu.be/GgLnwAwcbxU',
    'live_test_url' : 'https://probuseappdemo.com/probuse_apps/website_send_by_email/899',#'https://youtu.be/-fUxys12T7g',
    'category' : 'Sales/Sales',
    'depends': [
               'sale',
               'website_sale', 
               'sale_management', 
               'website',
               'website_sale_product_configurator'
               ],
    'data': [
            'views/website_view.xml',
            # 'views/header.xml',
            'data/mail_template_data.xml',
            'views/my_account_view.xml',
             ],
    'assets': {
        'web.assets_frontend': [
            'website_send_by_email/static/src/js/lib.js',
        ],
    },
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
