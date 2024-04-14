# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
##############################################################################

{
    "name" : "Equipment and Maintenance Request for Job Work Order in odoo",
    "version" : "17.0.0.0",
    "category" : "Projects",
    "depends" : ['base','hr_expense','bi_odoo_job_costing_management','stock'],
    'summary': 'Equipment Maintenance Request Integration of Job Order with Equipment Work order Maintenance Request Job Equipments Request Job Equipments Maintenance Request JOB order MRO machine MRO request job costing Maintenance MRO Maintenance job contracting MRO',
    'description': """
        Job Equipments Maintenance Request
        Job Equipments and Maintenance Request
        job contract, job contracting, Construction job , contracting job , contract estimation cost estimation project estimation , 
        This modules helps to manage contracting,Job Costing and Job Cost Sheet inculding dynamic material request
        Odoo job costing bundle
        Maintenance Request for job Equipments
        Job Equipments for project job costing
        Job Equipments for project costing
        Job Equipments for job costing
        Job Equipments for costing
        Project Job Costing and Job Cost Sheet.
        This modules helps to manage contracting,Job Costing and Job Cost Sheet inculding dynamic material request
        Project Contracting
        Project costing
        project cost sheet
		custom job order , custom job work order 
            Send Estimation to your Customers for materials, labour, overheads details in job estimation.
        Estimation for Jobs - Material / Labour / Overheads
        Material Esitmation
        Job estimation
        labour estimation
        Overheads estimation
        BrowseInfo developed a new odoo/OpenERP module apps.
        This module use for Real Estate Management, Construction management, Building Construction,
        Material Line on JoB Estimation
        Labour Lines on Job Estimation.
        Overhead Lines on Job Estimation.
        create Quotation from the Job Estimation.
        overhead on job estimation
        Construction Projects
        Budgets
        Notes
        Materials
        Material Request For Job Orders
        Add Materials
        Job Orders
        Bill of Quantity On Job Order
        Bill of Quantity construction
        Project job costing on manufacturing
    BrowseInfo developed a new odoo/OpenERP module apps.
    Material request is an instruction to procure a certain quantity of materials by purchase , internal transfer or manufacturing.So that goods are available when it require.
    Material request for purchase, internal transfer or manufacturing
    Material request for internal transfer
    Material request for purchase order
    Material request for purchase tender
    Material request for tender
    Material request for manufacturing order.
    product request, subassembly request, raw material request, order request
    manufacturing request, purchase request, purchase tender request, internal transfer request
""",
    "author": "BrowseInfo",
    "website" : "https://www.browseinfo.com",
    "price": 10,
    "currency": 'EUR',
    'live_test_url':'https://youtu.be/LrUB8Fj0UBY',
    "data": [
        'security/ir.model.access.csv',
        'views/euipment_request.xml',
    ],
    'qweb': [],
    'license': 'OPL-1',
    "auto_install": False,
    "installable": True,
    "images":['static/description/Banner.gif'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
