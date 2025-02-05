# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Asset/Equipment for Helpdesk Support System",
    'version': '7.1.6',
    'price': 19.0,
    'category': 'Services/Project',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This app allow helpdesk user to make request for Equipment for helpdesk ticket.""",
    'description':  """
Odoo Helpdesk Assets Equipment
Helpdesk Assets
Helpdesk Asset
Equipment
Helpdesk Equipment
ticket Equipment
support ticket Equipment

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
This module add website helpdesk support ticket.
Website Helpdesk Support Ticket
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
print Helpdesk Ticket
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

                    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/helpdesk_assets_equipment/733',#'https://youtu.be/OUQWn7vSEeM',
    'images':   [
                    'static/description/image.png'
                ],
    'depends':  [
                    'maintenance',
                    'website_helpdesk_support_ticket',
                ],
    'data': [
                    'security/ir.model.access.csv',
                    'security/assets_equipment_security.xml',
                    'data/ir_sequence_data.xml',
                    'views/helpdesk_assets_equipment_view.xml',
                    'views/maintenance_equipment_view.xml',
                    'views/helpdesk_support_view.xml',
            ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
