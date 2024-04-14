# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Schedule Activity Dashboard',
    'version': '6.0.7',
    'price': 69.0,
    'license': 'Other proprietary',
    'summary': """Dashboard for Schedule Activity""",
    'currency': 'EUR',

    'description': """
scheduled Activities
schedule Activity
scheduled Activity
planned activity
Schedule Activity Dashboard
Dashboard Schedule Activity
report Schedule Activity
Schedule Activity report
planned Activities
schedule_activity
Schedule Activity Management
activity manager
activity employee
user activity
employee activity
activity view
view activity
schedule an activity
Email activity
phone activity
call activity
meeting activity
followup activity
follow-up activity
call for demo
to do
reminder activity
activity reminder
exception activity
    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/s1.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/schedule_activity_dashboard/1357',
    'category': 'Discuss',
    'depends': [
                'mail',
                'base',
                'schedule_activity_global'
                ],

    'data': [
        'security/ir.model.access.csv',
        'views/schedule_activity_dashboard_view.xml',
        'views/activitys.xml',
    ],
    'installable': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
