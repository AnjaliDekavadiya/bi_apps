# -*- coding:utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
#See LICENSE file for full copyright and licensing details.

{
    'name': 'Machine Repair Request Import from Excel',
    'version': '8.1.4',
    'price': '19.0',
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category': 'Projects',
    'support': 'contact@probuse.com',
    'summary':  """Import machine repair requests from excel file.""",
    'description': """
This module import machine repair request from excel file.
Machine Repair Request Import from Excel
odoo repair
repair odoo 
machine repair
machine repair request import
    """,
    'images': ['static/description/img.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/machine_repair_request_import/475',#'https://youtu.be/uCE-WpOa9Z4',
    'external_dependencies': {'python': ['xlrd']},
    'depends': ['machine_repair_management'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/machine_repair_import_view.xml',
    ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
