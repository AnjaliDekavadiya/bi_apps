# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Create Sales Order from Material Requisitions",
    'version': '6.1.5',
    'category': 'Sales',
    'license': 'Other proprietary',
    'price': 149.0,
    'currency': 'EUR',
    'summary':  """Allow to create sales order from material requisition.""",
    'description': """
Material Requisitions Sales Order
Create Sales Order from Material Requisitions
    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/material_requisitions_sales_order/818',#'https://youtu.be/sz_rMldMy0Y',
    'depends': [
        'material_purchase_requisitions',
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/purchase_requisition_sale_order_wizard_view.xml',
        'views/purchase_requisition_view.xml',
    ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
