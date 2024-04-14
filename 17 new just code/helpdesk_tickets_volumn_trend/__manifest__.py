# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Tickets Volumn Trends for Helpdesk Support System',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'price': 19.0,
    'summary': """This app allow you to view tickets volumns for helpdesk support ticket system.""",
    'description': """
helpdesk ticket
ticket
ticket reports
helpdesk reporting trends
support ticket
helpdesk crm
Trends claim
claim order
support Trends
support ticket crm
Trends from ticket
ticket Trends
ticket Trends
helpdesk
odoo community helpdesk Trends
Trends helpdesk
Trends support
Trends team
helpdesk support ticket
support ticket
ticket volumn
ticket trend
helpdesk trend
helpdesk dashboard
helpdesk report
ticket support trend
trends
trend
odoo trend
support ticket report


    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/images.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/helpdesk_tickets_volumn_trend/630',#'https://youtu.be/_BAmW9D4Jac',
    'version': '5.4.2',
    'category' : 'Services/Project',
    'depends': [
        'website_helpdesk_support_ticket'
    ],
    'data':[
        'security/security.xml',
        'security/ir.model.access.csv',
        'report/report_helpdesk.xml',
        'views/view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
