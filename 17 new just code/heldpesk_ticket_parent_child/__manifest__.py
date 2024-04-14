# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Parent Child Support Tickets",
    'version': '5.5.1',
    'price': 52.0,
    'category': 'Services/Project',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This module allow you to create child tickets.""",
    'description':  """

parent ticket
child ticket
helpdesk ticket
parent child ticket
parent child helpdesk ticket
Website Helpdesk Support Ticket
helpdesk
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

helpdesk
help desk
helpdesk support system
website_support
crm_helpdesk
Helpdesk Management
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
project issue
claim
helpdesk
support system
suppor ticket
ticket
odoo helpdesk
child tickets
parent tickets
create child ticket
parent child ticketing
Parent-child ticketing
Parent child ticketing
parent child support ticket system

                    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    # 'live_test_url': 'https://youtu.be/SxfhiPEQ4w4',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/heldpesk_ticket_parent_child/254',#'https://youtu.be/-aFjEtYYq0o',
    'images':   [
                    'static/description/image.png'
                ],
    'depends':  [
                    'website_helpdesk_support_ticket',
                ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/heldpesk_ticket_child_wizard_view.xml',
        'views/helpdesk_support_view.xml',
            ],
   'installable' : True,
   'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
