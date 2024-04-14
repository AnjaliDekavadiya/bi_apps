# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Laundry Dry Cleaning Services App",
    'version': '4.1.6',
    'price': 109.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """Laundry Dry Cleaning Service Request and Management""",
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/laundry_iron_business/471',#'https://youtu.be/o56gx3VZOXc',
    'category' : 'Services/Project',
    'depends': [
                'project',
                'hr_timesheet',
                'portal',
                'sales_team',
                'stock',
                'sale_management',
                'website',
                ],
    'description': """
        Laundry Service Request
        Laundry Service Team
        Laundry Services
        Laundry Materials
        Laundry Service Products
        Laundry Workorders

    """,
    'data':[
        'security/laundry_service_security.xml',
        'security/ir.model.access.csv',
        'report/laubdry_service_request.xml',
        'datas/laundry_stages.xml',
        'datas/laundry_iron_sequence.xml',
        'datas/mail_template_ticket.xml',
        'views/laundry_service_support_view.xml',
        'views/laundry_request_template.xml',
        'views/hr_timesheet_sheet_view.xml',
        'views/support_team_view.xml',
        'views/my_laundry_request.xml',
        'views/successfull.xml',
        'views/task.xml',
        'views/feedback.xml',
        'views/thankyou.xml',
        'report/laundry_repair_analysis.xml',
        'views/product_template_view.xml',
        'views/product_consume_part_view.xml',
        'views/nature_of_service_view.xml',
        'views/repair_estimation_lines_view.xml',
        'views/menus.xml',
        'views/sale_order_view.xml',
        'views/stock_picking_view.xml',
        'views/laundry_stage_view.xml',
        'report/laundry_workorder.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'laundry_iron_business/static/src/js/laundry_service_js.js',
        ],
    },
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
