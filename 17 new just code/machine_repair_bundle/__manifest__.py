# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Machine Repair Bundle Apps',
    'price': 1.0,
    'version': '5.1.7',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This is package for Machine Repair Bundle.""",
    'description': """
Machine Repair Request and Management
repair management
machine_repair_industry
Machine Repair bundle
machine bundle
Machine Repair Management Odoo/OpenERP
all type of machine repair
machine repair website
website machine repair request by customer
Machine Repair industry
machine repair
fleet repair
car repair
bike repair
odoo repair
repair odoo
machine maintenance
maintenance odoo
repair maintenance
maintenance management
fleet maintenance
odoo maintenance
maintenance request
repair request
repair online
repair customer machine
customer machine repair
maintenance handling
Machine Repair Services
machine contract
machine location
machine equipments
machine repair location
machine repair contract
customer contract machine repair
machine repair contract
repair contract
machine contract repair
machine location for repair
customer machine repair location
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
#     'live_test_url': 'https://youtu.be/SlbnxqauQss',
    'category' : 'Services/Project',
    'depends': [
                 'machine_repair_management',
                 'machine_repair_material_requisition',
                 'machine_repair_job_costsheet',
                # 'machine_repair_with_contract',
                 'machine_repair_expense_claim',
                 'machine_repair_stock_inventory',
                 'machine_repair_job_inspection',
                 'machine_repair_request_import',
                 'machine_repair_equipment_integration',
                 'machine_repair_job_estimate',
                 'machine_repair_job_inspection_portal',
                ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
