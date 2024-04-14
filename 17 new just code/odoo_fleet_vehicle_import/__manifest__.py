# -*- coding:utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
#See LICENSE file for full copyright and licensing details.

{
    'name' : 'Fleet Vehicle Import from Excel',
    'version': '4.1.5',
    'price': '19.0',
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website' : 'www.probuse.com',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category': 'Human Resources',
    'support': 'contact@probuse.com',
    'summary':  """Import fleet vehicle from excel file.""",
    'description': """
This module import fleet vehicle from excel file.
Fleet Vehicle Import from Excel
fleet import
vehicle import
import fleets
import vehicles

    """,
    'images': ['static/description/img1.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/odoo_fleet_vehicle_import/762',#'https://youtu.be/Xw4THoVmH2s',
    'external_dependencies': {'python': ['xlrd']},
    'depends': ['fleet'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/fleet_vehicle_import_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
