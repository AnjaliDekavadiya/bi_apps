# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': ' Customer Invoice from Project Job Costing and Job Cost Sheet Progress Billing',
    'version': '17.0.0.0',
    'category': 'Accounting',
    'author': 'BrowseInfo',
    "price": 39,
    "currency": "EUR",
    'website': 'https://www.browseinfo.com',
    'summary': 'Apps for create customer invoice from job cost sheet invoice progress billing on project job costing invoice job costing progress billing job costing invoicing construction billing project construction Progress Billing invoice Customer Progress Billing',
    'description': """
        Project Job Costing and Job Cost Sheet. job costing progress billing , invoice on progress , Tax Invoice from Cost Sheet, invoice based on job sheet 
        This modules helps to manage contracting,Job Costing and Job Cost Sheet inculding dynamic material request , 
        Project Contracting
        Project costing
        project cost sheet , invoice from jobcosting , invoice from timesheet , Billing to Project Costing/Contracts , invoice to Project Costing/Contracts
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
    create customer invoice from the job cost sheet
    create customer invoice for job cost sheet
    Customer Invoice Based on Actual Purchase Qty
    Customer Invoice Based On Actual Vendor Bill Qty
    Customer Invoice Based Manual Invoice
""",
    'depends': ['bi_odoo_job_costing_management', 'bi_customer_progress_billing'],
    'data': [
        'security/ir.model.access.csv',
        'views/job_costing_view.xml',
        'wizard/job_costing_wizard_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'live_test_url': 'https://youtu.be/8XgHakKhxnk',
    "images": ['static/description/Banner.gif'],
    'license': 'OPL-1',
}
