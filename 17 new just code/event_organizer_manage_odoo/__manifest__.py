# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Event Management for Event Organiser',
    'version': '3.1.1',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """Event Organizer / Coordinator for Event Management""",
    'price': 89.0,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/eom.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/event_organizer_manage_odoo/1209',
    'category': 'Marketing/Events',
    'depends': [
        'odoo_job_costing_management',
        'job_cost_estimate_customer',
        'material_purchase_requisitions',
        'odoo_sale_estimates',
        'event',
        'calendar',
        ],
    'description': """
Event Organizer Management Odoo
    """,
    'data':[
        'security/ir.model.access.csv',
        'report/account_invoice_report_view.xml',
        'report/purchase_report_view.xml',
        'report/sale_report_view.xml',
        'report/project_report_view.xml',
        'wizard/checklist_template_wizard_view.xml',
        'views/event_checklist_type.xml',
        'views/checklist_template_view.xml',
        'views/event_menu_view.xml',
        'views/project_task_view.xml',
        'views/event_event_view.xml',
        'views/job_costing_view.xml',
        'views/purchase_requisition_view.xml',
        'views/sale_estimate_view.xml',
        'views/sale_order_view.xml',
        'views/account_move_view.xml',
        'views/purchase_order_view.xml',
        'views/calendar_view.xml',
        'views/estimate_report_view.xml',
        'views/report_invoice_view.xml',
        'views/sale_report_view.xml',
        'views/purchase_requisition_report_view.xml',
        'views/purchase_order_template.xml',
        'views/job_costing_report.xml',
        'views/stock_picking_view.xml',
        'views/purchase_quotation_template_report.xml',
        'views/res_partner_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
