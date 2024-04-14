# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
#    'name': 'Helpdesk Ticket Scan and Upload Photo by Customer and Technician',
    'name': 'Helpdesk Ticket Scan and Upload Photo by Customer',
    'currency': 'EUR',
    'version': '6.1.5',
    'category' : 'Services/Project',
    'license': 'Other proprietary',
    'price': 49.0,
    'summary': """This app allow your customers to Scan and Submit Images from Support Ticket my account menu.""",
    'description': """
scan
scan image
scan photo
photo scan
Website Helpdesk Support Ticket
helpdesk
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
helpdesk
help desk
helpdesk support system
website_support
crm_helpdesk
Helpdesk Management
helpdesk support
customer helpdesk
helpdesk
help desk
helpdesk support system
website_support
crm_helpdesk
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
image scan
photo
image
upload photo
upload image
photo upload
photo download
Scan and Upload Images for records
Uploaded Images Stored As Attachments and Also Chatter
Preview of Submitted Images
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': [
        'static/description/imag.png'
    ],
#    'live_test_url': 'https://youtu.be/ACDeNp77gMI',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/helpdesk_ticket_capture_photo/640', #'https://youtu.be/55iJmqm_cCc',
    'depends': [
        'website_helpdesk_support_ticket',
#        'helpdesk_agent_technician_portal',
        'base_capture_photo',
    ],
    'data':[
        'views/snap_image_template_view.xml',
#        'views/snap_image_template_technician_view.xml',
        'views/helpdesk_support_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
