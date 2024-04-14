# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Event Management by Organizer with Expenses and Timesheets',
    'version': '3.1.3',
    'currency': 'EUR',
    'price': 9.0,
    'license': 'Other proprietary',
    'category': 'Marketing/Events',
    'summary': """Event Management by Event Organizer with Expenses and Timesheets Feature""",
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/eoxt.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/event_organizer_expense_timesheet/1220',
    'depends': [
        'event_timesheet_tab_odoo',
        'event_organizer_manage_odoo',
        'hr_expense',
        ],
    'description': """
        Event Management by Event Organizer with Expenses and Timesheets Feature
    """,
    'data':[
        'views/event_view.xml',
        'views/hr_expense_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
