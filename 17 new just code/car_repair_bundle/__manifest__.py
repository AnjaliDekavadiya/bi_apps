# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.
{
    'name': 'CAR Repair Bundle Apps',
    'version': '4.1.5',
    'price': 1.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """Odoo CAR Repair bundle Apps.""",
    'description': """
car repair
repair car
car repair app

    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/crba.jpg'],
    'category' : 'Services/Project',
    'depends': [
            'car_repair_maintenance_service',
            'car_repair_material_requisition',
            'car_repair_fleet_integration',
            'car_repair_stock_inventory',
            'car_repair_estimate',
            'car_repair_job_costsheet',
            'car_repair_job_inspection',
            'car_repair_material_requisition_extend',
            'web_car_repair_multi_service',
               ],
    'data':[
      
    ],
    'installable' : True,
    'application' : False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
