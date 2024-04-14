# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Point of Sale POS Lock Period",
    'currency': 'EUR',
    'price': 49.0,
    'version': '5.2.2',
    'images': ['static/description/img.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/pos_lock_period/623',#'https://youtu.be/Qv6zWl83Y9w',
    'license': 'Other proprietary',
    'summary': """Allow you to lock Point of Sale POS during some time or period.""",
    'description': """
This module allows you to lock a POS base on period type.
Point of Sale POS Lock Period
point of sales lock
lock pos
pos lock
pos lock period
pos locking

    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'category' : 'Sales/Point Of Sale',
    'depends': [
        'point_of_sale',
    ],
    'data':[
        'security/ir.model.access.csv',
        'security/pos_security.xml',
        'views/pos_lock_period_view.xml',
        'views/menu.xml'
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
