# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
#See LICENSE file for full copyright and licensing details.

{
    'name': "Material Purchase Requisitions for Car Repair Request",
    'version': '7.5',
    'category': 'Services/Project',
    'license': 'Other proprietary',
    'price': 69.0,
    'currency': 'EUR',
    'summary':  """Material Purchase Requisitions for Car Repair Request.""",
    'description': """
Car Repair Material Requisition
Material Purchase Requisitions
Material Purchase
material request
Purchase Requisition
Requisition
product Requisition
car maintainance
car repair

    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/image1.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/car_repair_material_requisition/450',#'https://youtu.be/oNGIahF9mo8',

    'depends': ['material_purchase_requisitions',
                'car_repair_maintenance_service',
                ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/car_repair_material_requisition_view.xml',
        'views/car_repair_view.xml',
        'views/purchase_requisition_view.xml'
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
