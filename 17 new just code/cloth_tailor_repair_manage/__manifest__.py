# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Cloth Tailor with Repair Order',
    'version' : '5.1.3',
    'price' : 49.0,
    'currency': 'EUR',
    'category': 'Inventory/Inventory',
    'license': 'Other proprietary',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/cloth_tailor_repair_manage/220',#'https://youtu.be/8T6Tox8lcpE',
    'images': [
        'static/description/img.jpg',
    ],
    'summary' : 'This app integrates tailor business or tailor shop with Odoo Repair module of Odoo by using below listed features as per screenshots.',
    'description': """
This app integrates tailor business or tailor shop with Odoo Repair module of Odoo by using below listed features as per screenshots.
    - Allow you to configure the repair stage to manage your tailor request for repairing. Add a ‘Is Repair Stage’ field on cloth request stages.
    - You are allowed to create a new repair task and repair order from a tailor request.
    - For more details please check below screenshots and watch the video.
    """,
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website' : 'www.probuse.com',
    'depends' : [
        'repair',
        'cloth_tailor_management_odoo'
    ],
    'support': 'contact@probuse.com',
    'data' : [
        'security/ir.model.access.csv',
        'views/cloth_request_stage_view.xml',
        'wizard/cloth_repair_request_wizard_view.xml',
        'views/cloth_request_details_view.xml',
        'views/project_task_view.xml',
        'views/repair_order_view.xml'
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
