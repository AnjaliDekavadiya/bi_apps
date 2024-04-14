# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Share Notes on Portal Website',
    'version': '6.1.2',
    'category': 'Productivity/Notes',
    'price': 19.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'depends': [
        #'note',
        'project',
        'portal'
    ],
    'summary': 'Share Notes on Portal Website Odoo app',
    'description': """
This app allows you to share notes on the portal my account of your website. 
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/notes_share_portal/319',#'https://youtu.be/tcodmA2VFgY',
    'support': 'contact@probuse.com',
    'images': ['static/description/display.jpg'],
    'data': [ 
        'security/note_security.xml',
        'views/note_views.xml',
        'views/note_templates.xml'
        ],
    'installable': True,
    'application': False,
}
