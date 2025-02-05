# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Schedule Activity Management Extension',
    'version': '7.3.8',
    'price': 49.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """Extension of Scheduled Activities by Employee, Supervisor and Manager.""",
    'description': """
    Schedule Activity Global
This module allow you to show all scheduled Activities.
scheduled Activities
schedule Activity
scheduled Activity
planned activity
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
    # 'images': ['static/description/img1.jpg'],
    'images': ['static/description/image.png'],
    'live_test_url' : 'https://probuseappdemo.com/probuse_apps/schedule_activity_global/401',#'https://youtu.be/iHxeC5FkyU4',
    'category': 'Productivity/Discuss',
    'depends': [
                'mail',
                ],
    'data':[
        'security/scheduled_security.xml',
        'views/mail_activity_view.xml',
        'wizard/mail_activity_schedule.xml'
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
