# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.
{
    'name': 'Vendor Portal for Pricelists',
    'price': 69.0,
    # 'depends': ['website','sale_management','purchase'],
    'depends': ['portal','sale_management','purchase'],
    'category': 'Website/Website',
    'summary': 'Vendors to see the Product Pricelists from the My Account Portal from your website.',
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'https://www.probuse.com',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'version': '7.2.3',
    'description': """
Vendor Portal for Pricelists
vendor portal
portal vendor
vendor portal pricelist
portal pricelists

""",
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/image.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/vendor_pricelist_portal/101',#' https://youtu.be/DvPF9R9lDdU',
    'data': [
        # 'views/custom_comment.xml',
        # 'views/pricelist_portal_templates.xml',
        'views/new_pricelist_portal.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            '/vendor_pricelist_portal/static/src/js/product_comment.js',
        ],
    },
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
