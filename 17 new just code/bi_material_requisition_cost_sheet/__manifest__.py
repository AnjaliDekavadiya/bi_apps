# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Material Purchase Requisition and Cost Sheet Integration in odoo',
    'version': '17.0.0.0',
    'category': 'Projects',
    'summary': 'Apps Material Purchase Requisition Material Cost Sheet Integration product Purchase Requisition Material manufacturing Requisition Real Estate Management Construction contractor Material Request For Job Orders cost sheet Material Planning On Job Order',
    'description': """
        Project Job Costing and Job Cost Sheet.
        This modules helps to manage contracting,Job Costing and Job Cost Sheet inculding dynamic material request
        Project Contracting
        Project costing
        project cost sheet
        job contract, job contracting, Construction job , contracting job , contract estimation cost estimation project estimation , 
        This modules helps to manage contracting,Job Costing and Job Cost Sheet inculding dynamic material request
        Odoo job costing bundle
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
        Project Job Costing and Job Cost Sheet.
        This modules helps to manage contracting,Job Costing and Job Cost Sheet inculding dynamic material request
    ODOO Project Contracting Project costing project calculation project cost calculation constuction project costing 
    odoo project cost sheet construction material request odoo construction project management construction billing system construction cost calculation
    Odoo calculate  cost of construction project job contract job contracting Construction job contracting job contract estimation cost estimation project estimation 
    odoo modules helps to manage contracting Job Costing and Job Cost Sheet inculding dynamic material request
    Odoo job costing bundle job costing in construction project cost Estimation construction cost Estimation in Odoo 
    Odoo Send Estimation to your Customers for materials labour overheads details in job estimation.
    Odoo Estimation for Jobs - Material Labour Overheads Material Esitmation
    Odoo Job estimation labour estimation Overheads estimation
        BrowseInfo developed a new odoo/OpenERP module apps.
        This module use for odoo Real Estate Management Construction management Building Construction
    Odoo Material Line on JoB Estimation Labour Lines on Job Estimation Overhead Lines on Job Estimation.
    Odoo create Quotation from the Job Estimation overhead on job estimation Construction Projects
    Odoo Budgets Notes Materials Material Request For Job Orders Add Materials
    Odoo Job Orders Create Job Orders Job Order Related Notes Issues Related Project
    Odoo Vendors project construction Vendors Contractors
    Odoo Construction Management Construction Activity Construction Jobs
    Odoo Job Order Construction Job Orders Issues Job Order Notes
    Odoo Construction Notes Job Order Reports
    Odoo Construction Reports Job Order Note Construction app
    odoo Project Report Task Report
    Odoo Construction Project - Project Manager real estate property
    Odoo propery management bill of material
    Odoo Material Planning On Job Order Bill of Quantity On Job Order
    Odoo Bill of Quantity construction Project job costing on manufacturing
    BrowseInfo developed a new odoo/OpenERP module apps.
    Material request is an instruction to procure a certain quantity of 
    Odoo materials by purchase internal transfer or manufacturing.So that goods are available when it require.
    Odoo Material request for purchase, internal transfer or manufacturing
    Odoo Material request for internal transfer Material request for purchase order
    Odoo Material request for purchase tender Material request for tender
    Odoo Material request for manufacturing order.
    Odoo product request subassembly request raw material request order request
    Odoo manufacturing request purchase request purchase tender request internal transfer request
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
    "price": 39,
    "currency": "EUR",
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.com',
    'depends': ['base', 'bi_odoo_job_costing_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/material_requisition_cost_sheet_view.xml',
        'report/job_cost_sheet.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    "images": ['static/description/Banner.gif'],
    'live_test_url': 'https://youtu.be/85xBcKFWs1o',
}

