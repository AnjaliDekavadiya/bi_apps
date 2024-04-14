# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Email/Message Email History of Customers/Suppliers',
    'version': '7.25.1',
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'category' : 'Sales/Sales',
    'website': 'https://www.probuse.com',
    'summary' : 'This module will show email message history of customers/suppliers. Outgoing and Incoming emails history.',
    'price' : 9.0,
    # 'images': ['static/description/12.jpg'],
    'images': ['static/description/image.jpg'],
    #'live_test_url': 'https://youtu.be/PtM_po-9_q4',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/partner_email_history/1051',#'https://youtu.be/FEN8LNDKE_0',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'description': '''
Module will allows user to shows messaging/email history(Sent/Received)
for partner on partner form..
emails
customer email
supplier email
email history
email notes
send emails
received emails
partner email history
partner mail history
email history
customer email history
supplier email history
mail history
mail logs
mail server
mail synch
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
partner email
partner email history
email history
customer email
supplier email
customer email history
history email
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

