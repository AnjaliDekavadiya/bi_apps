# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Laundry Appointments for Collection and Delivery",
    'version': '4.1.3',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This app allow you to create laundry appointments for collection and delivery cloths.""",
    'price': 49.0,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/lma.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/laundry_meetings_appointments/473',#'https://youtu.be/e3WClwi7ILY',
    'category' : 'Services/Project',
    'depends': [
                'laundry_iron_business',
                'calendar'
                ],
    'description': """
Laundry Appointments for Collection and Delivery
laundry collection appoinment
laundry delivery appoinment
        
    """,
    'data':[
        'security/ir.model.access.csv',
        'security/laundry_service_security.xml',
        'wizard/calendar_meeting_view.xml',
        'views/laundry_service_support_view.xml',
        'views/calendar_event_view.xml',
        'views/menus.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
