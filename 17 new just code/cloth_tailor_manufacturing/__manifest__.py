# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Tailor App Integrate Manufacturing MRP',
    'version' : '5.1.3',
    'price' : 99.0,
    'currency': 'EUR',
    'category': 'Manufacturing/Manufacturing',
    'license': 'Other proprietary',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/cloth_tailor_manufacturing/217',#'https://youtu.be/FFGNoGgGXmw',
    'images': [
        'static/description/img.jpg',
    ],
    'description': """
This app integrates tailor business or tailor shop with Odoo manufacturing (MRP) module of Odoo by using below listed features as per screenshots.
    - Allow you to create your bill of materials to manage your tailor request from customers.
    - You are allowed to create a new BOM or use an existing BOM on tailor request and based on that system will allow you to create a manufacturing order.
    - Your tailor user should have manufacturing access to use MRP.
    - Using a bill of materials creates Manufacturing Orders & Work Orders directly from tailoring requests.
    - Manage your work order process for the tailor process in Odoo.
    - Showing BOM and Manufacturing order reference on tailor request.
    - For more details please check below screenshots and watch the video.
    """,
    'summary' : 'Cloths Tailor Management With Manufacturing MRP',
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website' : 'www.probuse.com',
    'depends' : [
        'mrp',
        'cloth_tailor_management_odoo'
    ],
    'support': 'contact@probuse.com',
    'data' : [
        'security/ir.model.access.csv',
        'views/cloth_request_details_view.xml',
        'views/mrp_production_view.xml',
        'views/mrp_bom_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
