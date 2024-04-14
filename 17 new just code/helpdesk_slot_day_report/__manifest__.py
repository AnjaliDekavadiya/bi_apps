# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.


{
    'name': 'Helpdesk Time Slot Report',
    'version': '5.1.34',
    'price': 49.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category': 'Services/Project',
    'summary': 'This app allow you to have report for time slots of helpdesk tickets.',
    'description': """
customer support
time slot
slot
slot time
support time slot
support slot
support request
support ticket
ticket
customer query
customer help
customer maintaince request
customer service request
website support ticket
website request customer

helpdesk
help desk
helpdesk support system
website_support
crm_helpdesk
helpdesk
help desk
helpdesk support system
website_support
crm_helpdesk
Helpdesk Management

claim order
project issue management
issue project management
project issuer
customer issue
customer feedback
customer case
customer project issue
odoo 11 project issue
project issue 11 odoo
project issue odoo 11
project task
support
project support
support manager
issue manager
issue operator​
odoo helpdesk
support system
community helpdesk



""",

    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/helpdesk_slot_day_report/489',#'https://youtu.be/Nopp_GAGdno',
    'images': ['static/description/image.png'],
    'depends': [
            'helpdesk_service_level_agreement'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/helpdesk_slot.xml',
        'views/helpdesk_lot_report.xml',
    ],

    'installable': True,
    'auto_install': False,
} 

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

