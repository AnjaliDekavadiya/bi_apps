# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
##############################################################################

{
    "name" : "Work Order Inspection for Job Costing",
    "version" : "17.0.0.0",
    "category" : "Projects",
    "depends" : ['base','hr_expense','bi_odoo_job_costing_management','bi_material_purchase_requisitions'],
    "author": "BrowseInfo",
    "website" : "https://www.browseinfo.com",
    'summary': 'Manage Inspections for Job order inspection for Contracting inspection for job order construction inspection for work order job costing inspection process for job costing Construction Job Costing inspection contracting job inspection for project costing',
    'description': """
        Project Job Costing and Job Cost Sheet.
        This modules helps to manage contracting,Job Costing and Job Cost Sheet inculding dynamic material request
        Project Contracting
        Project costing
        project cost sheet, Work Order Inspection, job Work Inspection, job inspection
        job contract, job contracting, Construction job Inspection , contracting job , contract estimation cost estimation project estimation , 
        This modules helps to manage contracting,Job Costing and Job Cost Sheet inculding dynamic material request
        Odoo job costing bundle , 
            Send Estimation to your Customers for materials, labour, overheads details in job estimation.
        Estimation for Jobs - Material / Labour / Overheads 
		
        Material Esitmation
        Job estimation , project inspection , work Inspection , job Inspection, 
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
        Material Planning On Job Order , quality check on order 

        Bill of Quantity On Job Order
        Bill of Quantity construction
        Project job costing on manufacturing
    BrowseInfo developed a new odoo/OpenERP module apps.
    Inspection Material request is an instruction to procure a certain quantity of materials by purchase , internal transfer or manufacturing.So that goods are available when it require.
    Material request for purchase, internal transfer or manufacturing
    Material request for internal transfer
    Material request for purchase order
    Material request for purchase tender
    Material request for tender
    Material request for manufacturing order.
    Inspection product request,Inspection subassembly request,Inspection raw material request,Inspection order request
    Inspection for job order
    inspection for work order
    job order inspection
    work order inspection
    constuction order inspection
    inspection for constuction management
    constuction management inspection
    inspection for construction management
    project inspection
    inspection on project job costing
""",
    "price": 29.00,
    "currency": 'EUR',
    "data": [
            'security/ir.model.access.csv',
            'security/groups.xml',
            'data/ir_sequence_data.xml',
            'views/job_inspection.xml',
            'report/job_instruction_temp_id.xml',
            'report/report_menu.xml',
    ],
    'qweb': [],
    "auto_install": False,
    'license': 'OPL-1',
    "installable": True,
    "live_test_url":'https://youtu.be/wFmQY7V_TJw',
    "images":['static/description/Banner.gif'],
}

