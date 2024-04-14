# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name' : 'POS Helpdesk RMA Return Merchandise Authorization',
    'version' : '4.2.2',
    'price' : 69.0,
    'currency': 'EUR',
    'category': 'Sales/Point of Sale',
    'license': 'Other proprietary',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/pos_return_order_rma_helpdesk/364',#'https://youtu.be/NLvJHG_9e-I',
    'images': [
        'static/description/image.jpg',
    ],
    'summary' : 'Point of Sales Helpdesk Tickets with RMA Return Merchandise Authorization',
    'description': """
        POS Helpdesk RMA Return Merchandise Authorization
        Helpdesk Support Ticket for POS and Create RMA
        Allow your POS helpdesk team to create RMA Order directly from ticket form.
        So when a customer posts a claim/ticket for POS order then from the backend helpdesk ticket form your support ticket users can create RMA from ticket form directly and then RMA flow will run into its process.
    """,
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website' : 'www.probuse.com',
    'depends' : [
        'helpdesk_support_ticket_pos',
        'pos_return_order_rma'
    ],
    'support': 'contact@probuse.com',
    'data' : [
        'security/ir.model.access.csv',
        'wizard/helpdesk_pos_rma_view.xml',
        'views/helpdesk_support_view.xml',
    ],
    'qweb': [
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
