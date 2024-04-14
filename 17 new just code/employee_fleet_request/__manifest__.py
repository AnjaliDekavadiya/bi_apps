# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Fleet Vehicle Request by Employee",
    'price': 19.0,
    'currency': 'EUR',
    'version': '7.1.54',
    'category' : 'Human Resources/Fleet',
    'license': 'Other proprietary',
    'summary' : 'This app allow your employee to request fleet or Vehicle in company.',
    'description': """
fleet request
fleet management
employee fleet
Employee Vehicle Request
Vehicle Requests
Fleet Repair Management
Vehicle Request
Manage Vehicle Requests From Employee
Request Employee Vehicle
FLEET VEHICLE
Fleet Vehicle Request
Vehicle Reservation Request
Vehicle Request Form
Fleet Request Form
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/employee_fleet_request/958',#'https://youtu.be/LhWw3nhebsc',
    'images': ['static/description/image.png'],
    'depends': [
        'fleet',
        'project',
        'hr',
        'resource',
    ],
    'data':[
        'security/ir.model.access.csv',
        'security/fleet_security.xml',
        'data/fleet_request_sequence.xml',
        'views/employee_fleet_view.xml',
        'views/fleet_request_report.xml',
        'views/fleet_vehicle_inherit.xml',
    ],
    'installable' : True,
    'application' : False,
    'auto_install' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

