# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Ticket from CRM Lead/Opportunity',
    'version': '5.6.1',
    'price' : 19.0,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'category' : 'Services/Project',
    'website': 'https://www.probuse.com',
    'summary' : 'This app allow yours CRM Users to create support ticket from Lead/Opportunity.',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'support': 'contact@probuse.com',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/helpdesk_ticket_crm_lead/593',#'https://youtu.be/m9laxj7oowc',
    'description': '''
helpdesk crm
crm claim
claim order
support crm
support ticket crm
lead from ticket
ticket crm
ticket lead
helpdesk
odoo community helpdesk
crm helpdesk
crm support
crm team
helpdesk support ticket
support ticket


    ''',
    'depends':[
        'website_helpdesk_support_ticket',
        'crm'
    ],
    'images':   [
            'static/description/image.png'
                ],

    'data' : [
        'security/ir.model.access.csv',
        'wizard/create_helpdesk_support_view.xml',
        'view/crm_view.xml',
        
        'view/helpdesk_support_view.xml',
        'security/security.xml'
    ],
    'installable':True,
    'auto_install':False
}

