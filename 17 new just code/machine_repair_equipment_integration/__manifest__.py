# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': "Machine Repair & Equipment Maintenance Integration",
    'version': '9.1.4',
    'category': 'Manufacturing/Maintenance',
    'license': 'Other proprietary',
    'price': 52.0,
    'currency': 'EUR',
    'summary':  """This module allow you to Machine Repair
    Equipment Integration.""",
    'description': """
Machine Repair Equipment Integration
Machine Repair
product repair
odoo repair
Equipment
repair Equipment
Equipment repair
Equipment machine repair
Maintenance request
Equipment Maintenance
Maintenance repair
repair Maintenance
    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/mrei.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/machine_repair_equipment_integration/472',#'https://youtu.be/uxBlVMDGLt8',

    'depends': [
        'machine_repair_management',
        'maintenance',
    ],

    'data': [
        'security/ir.model.access.csv',
        'wizard/maintenance_equipment_view.xml',
        'views/machine_repair_view.xml',
        'views/maintenance_equipment_view.xml',
        'views/maintenance_request_view.xml',
    ],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
