# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': "Website Job order-Work Order Portal for Construction Projects",
    'version': "17.0.0.0",
    "author": "BrowseInfo",
    "website" : "https://www.browseinfo.com",
    'category': "Projects",
    'summary': "Website work order portal website job order portal job costing work order portal job order contracting portal construction job order portal work order for construction Job Costing job contracting Construction job order Material Planning Job Order website",
    'description': """
        website job order
        website workorder
        website job order portal
        website work order portal
		easy to create work order create work order from website , create job work order from website portal , job order from portal , job order from portal 
		This module allow your customer/visitor to create job order or work order from your website.

- Anyone (Customers/Visitor/Internal Employees) can create job order or work order from your website.
- Customer can have portal in My Account to view and print job order they have created.
- Job order / Work order linked with Project so if they fill Project code [optional] then job order will be linked to Project.
- Instance notification to customer by email when job order created in system.

Job Work Order
Create Workorder
My Job Orders
        website constuction order
        Project Job Costing and Job Cost Sheet.
        This modules helps to manage contracting,Job Costing and Job Cost Sheet inculding dynamic material request
        Project Contracting
        Project costing
        project cost sheet
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
        NotesProject Job Costing and Job Cost Sheet.job contract, job contracting, Construction job , contracting job , contract estimation cost estimation project estimation , 
        This modules helps to manage contracting,Job Costing and Job Cost Sheet inculding dynamic material request
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
""",
    'data': [
        'views/job_order_view.xml',
        'views/website_workorder_templates.xml',
        'report/website_job_order.xml',
        'report/website_job_order_view.xml',
    ],
    'demo': [],
    "price": 5,
    'live_test_url': 'https://youtu.be/nS76vtwbit8',
    "currency": "EUR",
    'depends': ['base', 'sale_management', 'project', 'website', 'website_sale','hr_timesheet_attendance','bi_odoo_job_costing_management'],
    'installable': True,
    'auto_install': False,
    "images":['static/description/Banner.gif'],
    "license": "OPL-1",
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
