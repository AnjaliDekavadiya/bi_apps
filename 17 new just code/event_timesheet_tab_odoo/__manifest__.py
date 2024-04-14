# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Event with Timesheets Tab',
    'version' : '3.1.1',
    'price': 9.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': 'Timesheet Tab on Event Form in Odoo App',
    'description': """
This app allow your event manager/admin/user to fill the timesheet on event 
form and also allow your manager/users to fill timesheet related to event 
from timesheets menu as shown in below screenshots.    
""",
    'category': 'Marketing/Events',
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website':  'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/img.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/event_timesheet_tab_odoo/1176',
    'depends' : ['event','hr_timesheet',
    ],
    'data': [
        'views/account_analytic_line.xml',
        'views/event_event.xml'
    ],
    'installable': True,
    'application': False,   
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
