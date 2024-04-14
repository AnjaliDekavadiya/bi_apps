# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.
{
    'name': 'Material Requisition Bundle Apps',
    'version': '4.1.5',
    'price': 1.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """Odoo Material Requisition bundle Apps.""",
    'description': """
material purchase requisition
purchase requisition
requisition
material requisition

    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.png'],
    'category' : 'Warehouse',
    'depends': [
            'material_purchase_requisitions',
            'material_manufacturing_requisitions',
            'material_requisition_price_warning',
            'material_requisitions_sales_order',
            'material_requisition_stock_availibilty',
            'material_purchase_requisitions_analysis',
            'material_requisition_crm_opportunity',
            'project_task_material_requisition',
               ],
    'data':[
      
    ],
    'installable' : True,
    'application' : False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
