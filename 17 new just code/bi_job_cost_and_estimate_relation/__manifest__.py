# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sales Estimate from Job Cost Sheet in odoo',
    'version': '17.0.0.0',
    'category': 'Sales',
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.com',
    'summary': 'Sales Estimate on Job Cost Sheet Estimation for job costing sales estimation for job costing material estimation for construction sales estimation on construction estimation for materials cost estimation for construction Job estimation for sales Estimate',
    'description': """
	
	create Job Estimate from Job Cost Sheet,  job-costing calculations , sales forecaste from job cost sheet
        Project Job Costing and Job Cost Sheet.job contract, job contracting, Construction job , contracting job , contract estimation cost estimation project estimation , 
        This modules helps to manage contracting,Job Costing and Job Cost Sheet inculding dynamic material request
        This modules helps to manage contracting,Job Costing and Job Cost Sheet inculding dynamic material request
        Project Contracting
        Project costing,  create Sales Estimate from Job Cost Sheet , Sales Estimation , estimation based on job costing , estimation based on cost
        project cost sheet , sales forecasting,  Sales Estimate Create from Job Cost Sheet , job estimation from job costing sheet , work estimation from job cost sheet
		
            Send Estimation to your Customers for materials, labour, overheads details in job estimation.
        Estimation for Jobs - Material / Labour / Overheads
        cost estimation
        cost estimation for meterial
        cost estimation for labour
        cost estimation for overheads
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
        Create Job Orders
        Job Order Related Notes
        Issues Related Project
        Vendors
        Vendors / Contractors

        Construction Management
        Construction Activity
        Construction Jobs
        Job Order Construction
        Job Orders Issues
        Job Order Notes
        Construction Notes
        Job Order Reports
        Construction Reports
        Job Order Note
        Construction app
        Project Report
        Task Report
        Construction Project - Project Manager
        real estate property
        propery management
        bill of material
        Material Planning On Job Order

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
    sales estimation for job cost sheet
""",
    "price": 39,
    "currency": "EUR",
    'depends': ['bi_job_cost_estimate_customer','bi_odoo_job_costing_management','bi_material_purchase_requisitions'],
    'data': [
        'security/ir.model.access.csv',
        'views/relation_view.xml',
    ],
    'license':'OPL-1',
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/07cJVY7jTLI',
    "images":['static/description/Banner.gif'],
}
