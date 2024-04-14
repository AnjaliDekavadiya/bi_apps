{
    'name': 'Calendar Scheduler by Assignee on Working Hours',
    'version': '17.0.1.0',
    'summary': """New menu to schedule calendar meetings / events by assignee using FullCalendar Scheduler vertical resource view,
Odoo Calendar Configuration, Odoo Web Calendar Configuration,
Odoo Calendar Events, Odoo Calendar Meetings, Odoo Events, Odoo Meetings,
Odoo Calendar Resources, Odoo Calendar Schedulers, Odoo FullCalendar Schedulers,
Odoo FullCalendar Resources, Odoo Calendar Appointment,
Odoo Calendar Scheduler Assignees, Highlight Working Hours in Calendar View,
Odoo Calendar Configuration, Odoo Web Calendar Configuration, Odoo Calendar Events,
Odoo Calendar Meetings, Odoo Events, Odoo Meetings, Odoo Calendar Working Hours,
Odoo Calendar Business Hours""",
    'description': """
Calendar Resource by Assignee on Working Hours
==============================================

New menu to schedule calendar meetings / events by assignee and highlights or
restricts the working hours in calendar view. You need a license when using
the module commercially, see https://fullcalendar.io/license
""",
    'category': 'Productivity/Calendar',
    'author': 'MAC5',
    'contributors': ['MAC5'],
    'website': 'https://apps.odoo.com/apps/modules/browse?author=MAC5',
    'depends': [
        'calendar_resource_assignee_mac5',
        'calendar_working_hours_mac5',
    ],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': True,
    'images': ['static/description/banner.gif'],
    'price': -49.99,
    'currency': 'EUR',
    'support': 'mac5_odoo@outlook.com',
    'license': 'OPL-1',
    'live_test_url': 'https://youtu.be/zXc-u88d0n4',
}
