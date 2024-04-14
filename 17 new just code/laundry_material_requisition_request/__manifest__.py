# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Material Requisitions for Laundry Request',
    'version': '4.1.2',
    'price': 49.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """Material/Purchase Requisition for Laundry Request by Employee.""",
    'description': """
This module allowed you to create Material/Purchase Requisition From Laundry Request.
laundry 
laundry request
Purchase Requisitions
material Purchase Requisitions
material Purchase Requisition
laundry
laundry management

    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/image.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/laundry_material_requisition_request/91',#'https://youtu.be/QgObN6_whMU',
    'category': 'Services/Project',
    'depends': [
        'material_purchase_requisitions',
        'laundry_iron_business'
    ],
    'data':[
       'security/ir.model.access.csv',
       'wizard/laundry_request_material_requisitions_view.xml',
       'wizard/work_order_requisition_view.xml',
       'views/laundry_request_view.xml',
       'views/workorder_view.xml',
       'views/purchase_requisitions_view.xml'
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
