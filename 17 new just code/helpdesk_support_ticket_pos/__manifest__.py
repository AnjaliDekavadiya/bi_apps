# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name' : 'POS Helpdesk Customer Support',
    'version' : '4.1.2',
    'price' : 99.0,
    'currency': 'EUR',
    'category': 'Sales/Point of Sale',
    'license': 'Other proprietary',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/helpdesk_support_ticket_pos/47',#'https://youtu.be/NXzjZpfaIwY',
    'images': [
        'static/description/img.jpg',
    ],
    'summary' : 'POS Helpdesk Customer Support Ticket',
    'description': """
This app allows you to manage POS customer support tickets using a helpdesk ticket system as shown.
- This app allows you to manage your POS customer helpdesk tickets.
- Allow your POS team to manage helpdesk support ticket requests from customers.
- Allow your POS order related tickets from a helpdesk ticket system.
- This app is only for Odoo community edition.
- Allow your customer to create a ticket with POS reference as shown.
- Customer can create ticket with two way:
- By going into POS My Account Portal.
- Going into Direct Create Ticket from Website.
    """,
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website' : 'www.probuse.com',
    'depends' : [
        'website_portal_pos_orders',
        'website_helpdesk_support_ticket'
    ],
    'support': 'contact@probuse.com',
    'data' : [
        'views/template.xml',
        'views/helpdesk_view.xml'
    ],
    'qweb': [
    ],
    'assets': {
        'web.assets_frontend': [
            '/helpdesk_support_ticket_pos/static/src/js/helpdesk.js',
        ],
    },
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
