# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Helpdesk Team Email Alias',
    'version': '5.1.7',
    'category': 'Services/Project',
    'price': 39.0,
    'summary': 'Allow to set alias on team so when customer send mail to this it will automatically set this team on ticket.',
    'currency': 'EUR',
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website' : 'www.probuse.com',
    'support': 'contact@probuse.com',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/helpdesk_team_mail_alias/590',#'https://youtu.be/wkb9RTTPsno',
    'images': ['static/description/img.jpg'],
    'depends': [
        'website_helpdesk_support_ticket'
    ],
    'data': [
        'views/helpdesk_team_view.xml',
    ],
    'license': 'Other proprietary',
    'description': """
This app will allow to manage email aliases by helpdesk team.
helpdesk team
helpdesk
ticket
support ticket
help
support team
helpdesk team
team alias
helpdesk mail
helpdesk support email
team mail alias
    """,
    'installable': True,
    'auto_install': False,
}
