# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Subcontracting in Job Order / Construction / Contracting Industry in Odoo',
    'version': '17.0.0.0',
    'category': 'Projects',
    'summary': 'App for Construction Subcontracting in Job Order Subcontracting in Construction job costing Subcontracting Contracting Subcontracting costing Construction Job Costing construction Cost Sheet job contracting system Construction job order Material Planning',
    'description': """
        Project Job Costing and Job Cost Sheet.
        This modules helps to manage contracting,Job Costing and Job Cost Sheet inculding dynamic material request
        Project Contracting
        Project costing
        project cost sheet
        job contract, job contracting, Construction job , contracting job , contract estimation cost estimation project estimation , 
        This modules helps to manage contracting,Job Costing and Job Cost Sheet inculding dynamic material request

            Send Estimation to your Customers for materials, labour, overheads details in job estimation.
        Estimation for Jobs - Material / Labour / Overheads
        Material Esitmation
        Job estimation ,  Construction Subcontracting Construction project Subcontracting ,  Construction project Contracting , labor Contracting
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
    job order subcontracting
    subcontracting job order
    Subcontracting for constuction
    subcontracting for Contract management
    job order subcontracting management
    construction management for subcontracting management
    construction subcontracting
        
""",
    'author': 'BrowseInfo',
    "price": 10,
    "currency": "EUR",
    'website': 'https://www.browseinfo.com',
    'depends': ['base','web','website','portal','sale_management','project','purchase','account','bi_odoo_job_costing_management'],
    'data': [
        
            'security/ir.model.access.csv',
            
            'wizard/subcontract_from_jo_view.xml',
            'wizard/po_from_subcontract.xml',
            'views/job_subcontracting_view.xml',
            'views/job_subcontracting_menu.xml',
            'views/subcontract_portal_template.xml',
            
    ],
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    "images":['static/description/Banner.gif'],
    'live_test_url':'https://youtu.be/tbgfGnlW56E',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
