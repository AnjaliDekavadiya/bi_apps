# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Survey Answers View Portal',
    'version' : '5.1.3',
    'price' : 49.0,
    'currency': 'EUR',
    'category': 'Marketing/Surveys',
    'license': 'Other proprietary',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/survey_portal_odoo/112',#'https://youtu.be/uD0M3CuyFDE',
    'images': [
        'static/description/img.jpg',
    ],
    'summary' : 'Your to customer / portal user to view survey answers from the website to my account portal.',
    'description': """
This app allows your to customer / portal user to view survey answers from the website to my account portal.
    - Allow your customer / portal user see their own survey answers in my account portal of your website.
    - Allow your customer / portal user to view answers in detail using button print for their own survey answer.
    - For more details you can watch the video and check below screenshots.
    """,
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website' : 'www.probuse.com',
    'depends' : [
        'survey',
        'portal'
    ],
    'support': 'contact@probuse.com',
    'data' : [
        'views/template.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
