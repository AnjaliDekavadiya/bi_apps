# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

{
    'name': 'Website Address Autofill',
    'author': 'Softhealer Technologies',
    'website': 'https://www.softhealer.com',
    'support': 'support@softhealer.com',
    'category': 'Website',
    'license': 'OPL-1',
    'summary': "Address Auto Fill AutoFill Of Address Google places API In eCommerce Website Sale Address Auto Fill Based On Google Places Address Autofill Based On Google Places Auto Fill Street Auto Fill PIN Auto Fill Country Auto Fill State Odoo",
    'description': """This module allows to auto fill website address quickly. Once you configure google API key it auto fill address like street number, city, zip code, country & state.""",
    'version': '0.0.1',
    'depends': ['website_sale', 'portal'],
    'application': True,
    'data': [
        "views/website_views.xml",
        "views/website_sale_address_templates.xml",
        "views/portal_address_templates.xml"
    ],
    'assets': {
        'web.assets_frontend': [
            "sh_wsale_address_google_place/static/src/xml/sh_wsale_address_dropdown.xml",
            'sh_wsale_address_google_place/static/src/js/sh_wsale_address_autofill.js',
            'sh_wsale_address_google_place/static/src/scss/sh_wsale_address_autofill.scss',
        ],
        'website.assets_wysiwyg': [
            'sh_wsale_address_google_place/static/src/scss/sh_wsale_address_autofill.scss',
        ],
    },
    'auto_install': False,
    'installable': True,
    "images": ["static/description/background.png", ],
    'price': 25,
    'currency': 'EUR',
}
