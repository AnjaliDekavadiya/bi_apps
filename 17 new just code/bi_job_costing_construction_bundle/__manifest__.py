# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Job Costing Bundle (Contracting / Construction Management / Progress Billing / Estimates)',
    'version': '17.0.0.0',
    'category': 'Projects',
    'summary': 'Construction bundle Job Costing job contracting bundle Cost Sheet job contracting Construction job order Material Planning Construction Material request purchase Material request vendor Contractors job estimation construction waste project costing bundle',
    'description': """
    job contract, job contracting, Construction job , contracting job , contract estimation cost estimation project estimation , 
        This modules helps to manage contracting,Job Costing and Job Cost Sheet inculding dynamic material request
        Odoo job costing bundle
        job costing bundle management
        job contracting bundle
        construction management bundle
        sales project billing bundle
        sales customer process billing management
        sales esitmates bundle management
        all in one job contracting
        all in one sales contracting bundle
        ALL in one job costing
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
""",
    'author': 'BrowseInfo',
    "price": 10,
    "currency": "EUR",
    'website': 'https://www.browseinfo.com',
    'depends': ['bi_odoo_project_phases',
                'bi_odoo_job_costing_management',
                'bi_material_purchase_requisitions',
                'bi_job_costing_budget_contracting',
                'bi_job_equipments_maintenance_request',
                'bi_job_cost_and_estimate_relation',
                'bi_customer_progress_billing',
                'bi_job_costing_progress_billing',
                'bi_job_order_card_instruction',
                'bi_construction_contracting_change_order',
                'bi_material_requisition_cost_sheet',
                'bi_job_work_order_expense',
                'bi_hr_timesheet_sheet',
                'bi_job_inspection',
                'bi_website_project_request_for_information',
                'bi_website_construction_project',
                'bi_website_mobile_timesheet',
                'bi_website_job_workorder',
                'bi_odoo_job_subcontracting',
                'bi_construction_waste_management',
                'bi_project_team',
                'bi_mro_maintenance_management',
                'bi_construction_maintenance_equipment',
                'bi_issue_tracking_employee_portal',
                'bi_job_drawing_construction_contracting',
                'bi_job_drawing_image_contracting',
                'bi_job_costing_work_package',
                'bi_construction_contracting_issue_tracking',
                'bi_job_order_start_stop_timer',
                'bi_document_directory_extinsion_security',
                'bi_job_costing_contract_document',
                'bi_document_customer_portal',
                'bi_meeting_minutes_projects',
                'bi_document',
                'bi_construction_contracting_repair',
                'bi_transmittals_submittals_communication',
                'bi_project_notes_mobile_tablet',
                'bi_job_costing_dashboard',
                'bi_job_order_link_cost_sheet'
                ],  
    'data': [
        'views/hide_menu_item.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    "images":['static/description/Banner.png'],
}

