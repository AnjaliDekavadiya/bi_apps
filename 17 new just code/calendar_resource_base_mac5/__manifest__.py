{
    'name': 'FullCalendar Scheduler',
    'version': '17.0.2.1',
    'summary': """Base Module for FullCalendar Scheduler,
Odoo Calendar Configuration, Odoo Web Calendar Configuration,
Odoo Calendar Events, Odoo Calendar Meetings, Odoo Events, Odoo Meetings,
Odoo Calendar Resources, Odoo Calendar Schedulers, Odoo FullCalendar Schedulers,
Odoo FullCalendar Resources, Odoo Calendar Appointment""",
    'description': """
FullCalendar Scheduler
======================

This base module is used to build up calendar resources / schedulers in Odoo
using the FullCalendar Scheduler. This is for developers only. You need a
license when using the module commercially, see https://fullcalendar.io/license

NOTE: This has no functionality!
""",
    'category': 'Productivity/Calendar',
    'author': 'MAC5',
    'contributors': ['MAC5'],
    'website': 'https://apps.odoo.com/apps/modules/browse?author=MAC5',
    'depends': [
        'web_calendar_base_mac5',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/calendar_views.xml',
        'views/res_users_views.xml',
    ],
    'assets': {
        'web.assets_tests': [
            "calendar_resource_base_mac5/static/lib/fullcalendar/resource-timeline/main.css",
            "calendar_resource_base_mac5/static/lib/fullcalendar/timeline/main.css",
            "calendar_resource_base_mac5/static/lib/fullcalendar/resource-common/main.js",
            "calendar_resource_base_mac5/static/lib/fullcalendar/resource-daygrid/main.js",
            "calendar_resource_base_mac5/static/lib/fullcalendar/resource-timegrid/main.js",
            "calendar_resource_base_mac5/static/lib/fullcalendar/resource-timeline/main.js",
            "calendar_resource_base_mac5/static/lib/fullcalendar/timeline/main.js",
        ],
        'web.assets_backend': [
            'calendar_resource_base_mac5/static/src/css/**/*',
            'calendar_resource_base_mac5/static/src/js/**/*',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.png'],
    'price': 199.99,
    'currency': 'EUR',
    'support': 'mac5_odoo@outlook.com',
    'license': 'OPL-1',
}
