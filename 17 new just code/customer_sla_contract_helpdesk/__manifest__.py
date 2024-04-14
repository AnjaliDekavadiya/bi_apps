# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Service Level Agreements to Customer for Helpdesk/Support",
    'depends': ['contract_recurring_invoice_analytic', 'helpdesk_service_level_agreement'],
    'price': 49.0,
    'version': '5.3.2',
    #'live_test_url':'https://youtu.be/XE8hiAWMQHg',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/customer_sla_contract_helpdesk/803',#'https://www.youtube.com/watch?v=n4Etzi8qIU8',
    'currency': 'EUR',
    'category' : 'Sales/Sales',
    'license': 'Other proprietary',
    'summary': """This app allow you to create service level agreements and print and send your customer by agreeing SLA level.""",
    'description': """
​Customer Sla Contract Helpdesk
SLA Levels
Service Level Agreements
Service Level
SLA Team
Service Level Team
Team SLA
Service Level Contract
Internet Service Provider
SLA Level
Helepdesk SLA level
Helepdesk Service Level Agreements
SLA Level
Service Team
SLA Analysis
Helpdesk SLA Analysis
Help Desk Service Level Agreement (SLA)
SLA
service level agreement
helpdesk sla
sla helpdesk
support sla
sla support
service-level agreement
Service-based SLA
IT help desks
customer service organizations
* INHERIT helpdesk.support.form.inherit.history (form)
* INHERIT res.partner.form.level.config (form)
Helpdesk Service Level Agreement (form)
Helpdesk Service Level Agreement (tree)
Helpdesk Service Level Agreement Search (search)
helpdesk.level.config.form (form)
helpdesk.level.config.select (search)
helpdesk.level.config.tree (tree)
helpdesk.stage.history.form (form)
helpdesk.stage.history.select (search)
helpdesk.stage.history.tree (tree)
- Allow to you to setup SLA Levels under configuration.

- Allow you to link SLA level on your Customer form.

- Calculating Deadline of tickets based on SLA level configuration. System allow you to setup SLA level by selecting Category of ticket and priority based on that you can configure number of Hours/Day/Week to have automatic Deadline on Tickets.

- Helpdesk SLA Team: You can setup support team with their Working Time/Calendar and setup Estimated Response Time / Reply Time / Working Time for that stage.

- View SLA time logs for that ticket on helpdesk form based on Helpdesk SLA Team setup.

- Helpdesk SLA Analysis to anlysis your SLA logs by ticket numbers.

- For more details you can contact us or watch Video.
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
unique ticket number to customer automatically
being able to reply to incoming emails to communicate with customer
seeing all a customer's incoming help desk requests in context against customer object
unique ticket number per issue
Website Support Ticket Invoice:
customer support Invoice
support request Invoice
support ticket Invoice
ticket Invoice
customer query 
customer help
customer maintaince request Invoice
customer service request Invoice
website support ticket Invoice
website request customer Invoice
ticket invoice 
customer invoice for support tickets
Website Support Ticket My Account:
Customer Portal (My Account) - Support Tickets
customer support Portal
support request Portal
support ticket Portal
ticket Portal
customer query 
customer help
customer maintaince request Portal
customer service request Portal
website support ticket Portal
website request customer Portal
ticket Portal 
customer Portal for support tickets
helpdesk
help desk
helpdesk support system
website_support
crm_helpdesk
Helpdesk Management
unique ticket number to customer automatically
being able to reply to incoming emails to communicate with customer
seeing all a customer's incoming help desk requests in context against customer object
unique ticket number per issue
Website Support Ticket Timesheet:
Customer Portal (Timesheett) - Support Tickets
odoo helpdesk
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


    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/image.png'],
    'data':[
        'views/contract_sla_view.xml',
        'views/account_view.xml',
        'views/contract_sla_report.xml',
        'report/sla_level_report.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
