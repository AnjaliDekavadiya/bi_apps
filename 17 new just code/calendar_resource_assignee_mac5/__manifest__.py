{
    'name': 'Calendar Scheduler by Assignee',
    'version': '17.0.1.1',
    'summary': """New menu to schedule calendar meetings / events by assignee using FullCalendar Scheduler vertical resource view,
Odoo Calendar Configuration, Odoo Web Calendar Configuration,
Odoo Calendar Events, Odoo Calendar Meetings, Odoo Events, Odoo Meetings,
Odoo Calendar Resources, Odoo Calendar Schedulers, Odoo FullCalendar Schedulers,
Odoo FullCalendar Resources, Odoo Calendar Appointment,
Odoo Calendar Scheduler Assignees""",
    'description': """
Calendar Resource by Assignee
=============================

New menu to schedule calendar meetings/ events by assignee. You need a license
when using the module commercially, see https://fullcalendar.io/license
""",
    'category': 'Productivity/Calendar',
    'author': 'MAC5',
    'contributors': ['MAC5'],
    'website': 'https://apps.odoo.com/apps/modules/browse?author=MAC5',
    'depends': [
        'calendar_resource_base_mac5',
    ],
    'data': [
        'views/calendar_views.xml',
        'views/res_users_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'calendar_resource_assignee_mac5/static/src/js/**/*',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
    'price': 200.00,
    'currency': 'EUR',
    'support': 'mac5_odoo@outlook.com',
    'license': 'OPL-1',
    'live_test_url': 'https://youtu.be/zscXXkvI-y8',
}
