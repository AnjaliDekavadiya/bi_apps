# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Car Repair Request with Multi Services",
    'summary': """This app allow your customer to select multiple services on car repair request""",
    'description': """
Allow you to add multiple services on create maintenance service request
car repair
repair car
    """,
    'currency': 'EUR',
    'price': 99.0,
    'version': '6.1.4',
    'license': 'Other proprietary',
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/web_car_repair_multi_service/460',#'https://youtu.be/AIaGGCA4Bw4',
    'category' : 'Services/Project',
    'depends': [
            'car_repair_maintenance_service',
    ],
    'data':[
        'views/car_repair_maintenance_service_view.xml',
        'views/car_repair_service_template.xml',
    ],
    'assets': {
            'web.assets_frontend': [
                'web_car_repair_multi_service/static/src/js/car_repair_maintenance_service_js.js',
        ],
    },
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
