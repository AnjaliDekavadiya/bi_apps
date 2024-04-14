# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
{
    'name': "Vehicle Rental Management | Car Rent | Car Rental Management",
    'version': "1.5",
    'description': "A car rental, hire car or car hire agency is a company that rents automobiles for short periods.",
    'summary': "Vehicle Rental Management",
    'author': 'TechKhedut Inc.',
    'website': "https://techkhedut.com",
    'depends': ['mail', 'contacts', 'product', 'fleet', 'sale_management'],
    'data': [
        # data
        'data/vehicle_product_data_views.xml',
        'data/sequence_views.xml',
        'data/vehicle_rental_mail_template.xml',
        'data/report_paper_format.xml',
        'data/ir_cron.xml',
        # Security
        'security/ir.model.access.csv',
        # Wizards
        'wizards/vehicle_damage_views.xml',
        # Views
        'views/assets.xml',
        'views/model_views.xml',
        'views/vehicle_contract_views.xml',
        'views/customer_document_views.xml',
        'views/cancellation_policy_views.xml',
        'views/rental_vehicle_image_views.xml',
        'views/insurance_policy_views.xml',
        'views/extra_service_views.xml',
        'views/vehicle_damage_image_views.xml',
        'views/vehicle_payment_option_views.xml',
        # Reports
        'report/vehicle_contract_report_views.xml',
        'report/scratch_report_views.xml',
        # Menus
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'vehicle_rental/static/src/xml/template.xml',
            'vehicle_rental/static/src/css/lib/style.css',
            'vehicle_rental/static/src/css/style.scss',
            'vehicle_rental/static/src/js/vehicle_rental_dashboard.js',
        ],
    },
    'images': ['static/description/cover.gif'],
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 110,
    'currency': 'EUR',
}
