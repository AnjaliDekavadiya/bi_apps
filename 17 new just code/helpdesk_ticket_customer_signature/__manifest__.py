# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.
{
    'name': "Signature of Customer on Helpdesk Ticket",
    'price': 69.0,
    'version': '6.2.6',
    'category': 'Services/Project',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This module allow your customer to signature on helpdesk ticket on portal.""",
    'description':  """
Odoo Helpdesk Ticket Customer Signature
Website Helpdesk Support Ticket
helpdesk
customer signature
digital signature
signature
helpdesk signature
support signature
client signature
client agreement
sign
document signature
document sign
helpdesk support
customer helpdesk
customer Helpdesk support
Helpdesk support request
Helpdesk support ticket
ticket
Helpdesk customer query
Helpdesk customer help
Customer Maintaince request
Customer service request
Website Helpdesk ticket
website request customer
customer support
support request
support ticket
ticket
customer query
customer help
customer maintaince request
customer service request
website support ticket
website request customer
customer support
support request
support ticket
ticket
customer query
customer help
customer maintaince request
customer service request
website support ticket
website request customer
support timesheet
support time
support hr timesheet
employee timesheet
Website Helpdesk Support Ticket

​project issue
issue project
project helpdesk
project case
project claim
claim order
project issue management
issue project management
project issuer
customer issue
customer feedback
customer case
customer project issue
odoo 11 project issue
project issue 11 odoo
project issue odoo 11
project task
support
project support
support manager
issue manager
issue operator​


                    
                    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    # 'live_test_url': 'https://youtu.be/Zg43aD-i3IE',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/helpdesk_ticket_customer_signature/244',#'https://youtu.be/a8CQ5a4reE0',
    'images':   [
        'static/description/image.png'
    ],
     'depends':  [
#        'helpdesk_agent_technician_portal',
        'website_helpdesk_support_ticket',
    ],
    'data': [
            # 'data/send_thankyou_mails.xml',
            # 'data/send_signature_request_emails.xml',
            'data/send_thankyou_mails_new.xml',
            'data/send_signature_request_emails_new.xml',
            # 'data/send_thankyou_mail.xml',
            # 'data/send_signature_request_email.xml',
            'views/helpdesk_support_view.xml',
            'views/helpdesk_ticket_customer_signature_view.xml',
#            'views/helpdesk_ticket_customer_signature_view_technician.xml',
    ],
   'installable' : True,
   'application' : False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
