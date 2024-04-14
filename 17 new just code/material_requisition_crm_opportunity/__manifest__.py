# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Product/Material Purchase Requisitions from CRM Opportunity',
    'version': '4.1.6',
    'price': '25.0',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """Allow to create Material Purchase requisition from CRM.""",
    'description': """
Material Purchase Requisitions
material requisition
material purchase requisition
This module allowed you to create Material/Purchase requisition From Crm Module.
    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpeg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/material_requisition_crm_opportunity/688',#'https://youtu.be/G-6ZrLm-Nbs',
    'category': 'Warehouse',
    'depends': [
                'material_purchase_requisitions',
                'crm'
                ],
    'data':[
       'security/ir.model.access.csv',
       'wizard/crm_lead_material_requisition_view.xml',
       'views/crm_lead_view.xml',
       'views/purchase_requisitions_view.xml'
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
