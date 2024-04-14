# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Email/Message History Of Customers/Suppliers',
    'version': '1.0',
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'category' : 'Tools',
    'website': 'https://www.probuse.com',
    'summary' : 'This module will show email history of customers/suppliers. Outgoing and Incoming emails history.',
    'price' : 17.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'description': '''
Module will allows user to shows messaging/email history(Sent/Received)
for partner on partner form..

Tags:
emails  
customer email
supplier email
email history
email notes
send emails
received emails
track emails in odoo
odoo email
email tracking
odoo email history
email logs
logs of emails
customer logs
supplier logs
customer communication
communication history
chatter messages
chatter emails
  ''',
    'depends':[
        'mail', 'sales_team'
    ],
    'data' : [
        'views/partner_view.xml',
        'views/mail_message_view.xml',
    ],
    'installable':True,
    'auto_install':False
}

