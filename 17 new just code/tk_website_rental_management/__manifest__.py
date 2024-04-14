# -*- coding: utf-8 -*-
#############################################################################
#
#    TechKhedut Inc.
#
#    Copyright (C) 2023-TODAY TechKhedut (<https://www.techkhedut.com>)
#    Author: TechKhedut(<https://www.techkhedut.com>)
#    Part of TechKhedut. See LICENSE file for full copyright and licensing details.
#
#############################################################################
{
    'name': 'Property Management Website | Property Rental Website | Theme Rental Management | Real Estate Website | Property Sale Website',
    'description': 'Property Sale & Rental Website',
    'summary': 'Property Sale & Rental Website',
    'category': 'Website',
    'version': '2.0',
    'author': 'TechKhedut Inc.',
    'company': 'TechKhedut Inc.',
    'category': 'Website',
    'maintainer': 'TechKhedut Inc.',
    'website': "https://www.techkhedut.com",
    'depends': [
        'web',
        'crm',
        'rental_management',
        'portal',
        'website',
        'website_blog',
        'website_mass_mailing'
    ],
    'data': [
        # data
        'data/data.xml',
        # security
        'security/ir.model.access.csv',
        # backend
        'views/backend/property_theme_config.xml',
        'views/backend/property_details.xml',
        # templates
        'views/assets.xml',
        'views/footer.xml',
        'views/header.xml',
        'views/home.xml',
        'views/listing.xml',
        'views/property_details.xml',
        'views/my_portal.xml',
        'views/map_view.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'tk_website_rental_management/static/src/scss/colors.scss',
            'tk_website_rental_management/static/src/css/reset.css',
            'tk_website_rental_management/static/src/css/plugins.css',
            'tk_website_rental_management/static/src/css/style.css',
            'tk_website_rental_management/static/src/css/color.css',
            'tk_website_rental_management/static/src/js/plugins.js',
            'tk_website_rental_management/static/src/js/scripts.js',
            'tk_website_rental_management/static/src/js/website_rental.js',
            'tk_website_rental_management/static/src/js/map-single.js',
            'tk_website_rental_management/static/src/js/map-plugins.js',
            'tk_website_rental_management/static/src/js/map-listing.js',
        ],
        'web._assets_primary_variables': [
            'tk_website_rental_management/static/src/scss/primary_variables.scss',
        ],
    },
    'images': [
        'static/description/property-rental.gif',
    ],
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 274,
    'currency': 'USD',
}
