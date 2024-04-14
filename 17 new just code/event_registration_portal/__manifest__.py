# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Event Registration Portal for Customer",
    'version': '6.1.3',
    'license': 'Other proprietary',
    'price': 39.0,
    'currency': 'EUR',
    'summary':  """This app allows your customers to view event registrations on my account portal of your website.""",
    'description': """

       This app allows your customers to view event registrations on my account portal of your website.
Event Registaration Portal
Customer / Portal Event
Registration Portal

    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img14.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/event_registration_portal/474',#'https://youtu.be/BSaEPahAIrU',
    'category': 'Marketing/Events',
    'depends': ['event','portal','website','event_sale'],
    'data': [
            'security/ir.model.access.csv',
            'security/ir_rule.xml',
            'views/event_regi_portal_templates.xml',
            ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
