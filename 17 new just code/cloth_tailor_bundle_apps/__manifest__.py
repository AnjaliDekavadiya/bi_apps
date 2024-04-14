# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Bundle of Clothes Tailor Related Apps",
    'version': '3.1.2',
    'price': 1.0,
    'currency': 'EUR',
    'category' : 'Sales/Sales',
    'license': 'Other proprietary',
    'summary': """This module contains bundle of Clothes Tailor Related Apps/Modules.""",
    'description': """
Clothes Tailor Related apps
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/cb.png'],
    'depends': [
        'cloth_tailor_management_odoo',
        'cloth_tailor_job_costsheet',
        'cloth_tailor_material_requisition',
        'cloth_tailor_manufacturing',
        'cloth_tailor_picking_manage',
        'cloth_tailor_team_manage',
        'cloth_tailor_repair_manage',
    ],
    'data':[
        
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
