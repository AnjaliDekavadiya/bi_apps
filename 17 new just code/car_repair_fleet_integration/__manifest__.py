# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Car Repair Integration Fleet App',
    'version': '7.2.5',
    'price': 59.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This module allow you to create vehicle and vehicle service.""",
    'description': """
Car Repair Fleet Integration
This module allow you to create vehicle and vehicle service from car repair.
car repair
repair car
fleet
car fleet

    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/img.jpg'],
    'live_test_url' : 'https://probuseappdemo.com/probuse_apps/car_repair_fleet_integration/458',#'https://youtu.be/yLRkNNoEQB0',
    'category': 'Services/Project',
    'depends': [
        'car_repair_maintenance_service',
        'fleet_product_link',
                ],
    'data':[
        'security/ir.model.access.csv',
        'security/security.xml',
        'wizard/car_service_view.xml',
        'wizard/fleet_vehicle_view.xml',
        'views/car_repair_type_view.xml',
        'views/car_repair_support_view.xml',
        'views/fleet_vehicle_log_services_view.xml',
        'views/fleet_vehicle_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
