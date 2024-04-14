# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Point of Sales POS Customer Feedback Rating',
    'version': '5.2.1',
    'category': 'Sales/Point Of Sale',
    'price': 79.0,
    'currency': 'EUR',
    'summary': """Allow your customer to give feedback and rating for POS orders.""",
    'description': """
This mpdule will allow you to to POS customer feedback rating.
POS feedback
pos rating
point of sales rating
point of sale rating
point of sale feedback
point of sales feedback
customer feedback
client feedback
client pos feedback
client point of sale feedback
Point of Sales POS Customer Feedback Rating
Allow your customer to give feedback and rating for POS orders
    """,
    'license': 'Other proprietary',
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/pos_customer_feedback_rating/619',
    'images': ['static/description/images.jpg'],
    'support': 'contact@probuse.com',
    'depends': [
        'point_of_sale',
        'website',
        'pos_order_report',
    ],
    'data': [
        'data/mail_template.xml',
        'views/feedback.xml',
        'views/pos_order_view.xml',
        'views/res_partner_view.xml'
    ],
    'installable': True,
    'auto_install': False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
