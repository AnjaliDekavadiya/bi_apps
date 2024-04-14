# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Car Repair and Material Requisition Extension',
    'version': '6.1.4',
    'price': 99.0,
    'currency': 'EUR',
    'category': 'Services/Project',
    'license': 'Other proprietary',
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'images' : ['static/description/image.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/car_repair_material_requisition_extend/454',#'https://youtu.be/QYaHEIdDRPw',
    'summary':  """Allow you to set Car Repair Reference on Purchase Order and Stock Inventory Picking.""",
    'description': '''
Car Repair Material Requisition Extend.
This module allow you to set Car Repair Reference on Purchase Order and Inventory Picking.
Car Repair and Material Requisition Extension
''',
    'support': 'contact@probuse.com',
    'depends': [
                'car_repair_material_requisition',
                'car_repair_stock_inventory',
                'project_task_material_requisition',
               ],
    'data': [
            'views/purchase_order_view.xml',
             ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
