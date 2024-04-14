{
    'name': 'Calendar Working Hours',
    'version': '17.0.1.0',
    'summary': """Highlight Working Hours in Calendar View,
Odoo Calendar Configuration, Odoo Web Calendar Configuration, Odoo Calendar Events,
Odoo Calendar Meetings, Odoo Events, Odoo Meetings, Odoo Calendar Working Hours,
Odoo Calendar Business Hours""",
    'description': """
Calendar Working Hours
======================

This module highlights the working hours in calendar view
""",
    'category': 'Productivity/Calendar',
    'author': 'MAC5',
    'contributors': ['MAC5'],
    'website': 'https://apps.odoo.com/apps/modules/browse?author=MAC5',
    'depends': [
        'resource',
        'web_calendar_base_mac5',
    ],
    'data': [
        'views/res_config_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'calendar_working_hours_mac5/static/src/js/**/*',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
    'price': 149.99,
    'currency': 'EUR',
    'support': 'mac5_odoo@outlook.com',
    'license': 'OPL-1',
    'live_test_url': 'https://youtu.be/7ZO-ciGkrq4',
}
