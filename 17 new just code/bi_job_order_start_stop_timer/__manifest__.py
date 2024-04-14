# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Job/Work Order Start and Stop Timer and Digital Signature in Odoo',
    'version': '17.0.0.0',
    'category': 'Project',
    'summary': 'Job Order timer Work Order timer Start and Stop Timer for job order Digital Signature for job costing job order start and stop timer job work order start stop timer start job order with timer Digital Signature for job costing construction Cost Sheet',
    "description": """
BrowseInfo developed a new odoo/OpenERP module apps.
Job / Work Order Start and Stop Timer and Digital Signature
job order start and stop timer
work order start stop timer
job work order start stop timer
work order timer
start workorder 
start job order

This app help employees to set Duration By buttons and it will allowed customer to sign on job order.
""",
    'author': 'BrowseInfo',
    'price': 89,
    'currency': "EUR",
    'website': 'https://www.browseinfo.com',
    'live_test_url': 'https://youtu.be/z5TFC80Jx1o',
    'depends': ['base', 'bi_website_mobile_timesheet', 'bi_material_purchase_requisitions',
                'bi_odoo_job_costing_management'],
    'data': [
        'views/website_job_order_template.xml',
        'views/work_order_history.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            'bi_job_order_start_stop_timer/static/src/js/date_time_show.js',
        ],
    },
    'demo': [],
    'test': [],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    "images": ["static/description/Banner.gif"],
}
