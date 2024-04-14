# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': "Transmittals and Submittals Document for Construction Job Costing",
    'version': "17.0.0.0",
    'category': "Projects",
    'summary': "Transmittals document on Construction Submittals Document for Construction Transmittals document on Job Contracting Transmittals document for job costing document Submittals for job costing contracting document transmission construction document submission",
    'description': """ Transmittals Communications Submittals Communications Transmittals Submittals Communications """,
    'author': "BrowseInfo",
    "website": "https://www.browseinfo.com",
    "price": 19,
    "currency": 'EUR',
    'depends': ['base', 'project', 'bi_odoo_job_costing_management', 'bi_material_purchase_requisitions'],
    'data': [
        'security/ir.model.access.csv',
        'data/transmitttal_email_templete.xml',
        'reports/transmittal_submittal_report.xml',
        'reports/transmittal_submittal_templete.xml',
        'views/configuration_view.xml',
        'views/transmittal_submittal_view.xml',
    ],
    'license': 'OPL-1',
    'currency': "EUR",
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    "live_test_url": 'https://youtu.be/5cfsd_wkMDA',
    "images": ['static/description/Banner.gif'],
}

