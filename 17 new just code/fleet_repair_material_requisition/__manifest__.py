# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Material Purchase Requisitions for Fleet Repair Request',
    'version': '7.1.5',
    'price': 39.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """Material/Purchase Requisition for Fleet Repair Request by Employee.""",
    'description': """
This module allowed you to create Material/Purchase Requisition From Fleet Repair Request.
fleet repair
fleet repair request
Purchase Requisitions
material Purchase Requisitions
material Purchase Requisition
fleet
vehicle
vehicle repair
fleet repair management

    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/image.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/fleet_repair_material_requisition/723',#'https://youtu.be/lAnG9mh1kMk',
    'category': 'Human Resources/Fleet',
    'depends': [
        'material_purchase_requisitions',
        'fleet_repair_request_management'
    ],
    'data':[
       'security/ir.model.access.csv',
       'wizard/fleet_request_material_requisition_view.xml',
       'views/fleet_request_view.xml',
       'views/purchase_requisitions_view.xml'
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
