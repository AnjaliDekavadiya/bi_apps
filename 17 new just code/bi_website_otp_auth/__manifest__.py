# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Website OTP Verification',
    'version': '17.0.0.0',
    'category': 'Website',
    'summary': 'Signup OTP verification signup email verification Website OTP Authentication signup email authentication signup OTP authentication Odoo OTP authentication sing-in OTP authentication sign up verification via email verification for login OTP Authentication',
    'description' :"""
        
        Website OTP Authentication in odoo,
        OTP Expire Timer in odoo,
        Send OTP to Email Address in odoo,
        Set OTP Time Limit in odoo,
        Set OTP Type in odoo,
        Select Email Verification Method in odoo,
        Enable Sign-in Authentication in odoo,
        Enable Sign-up Authentication in odoo,
        OTP Validation in odoo,       
    
    """,
    'author': 'BrowseInfo',
    "price": 18,
    "currency": 'EUR',
    'website': 'https://www.browseinfo.com',
    'depends': ['base', 'website','web'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/otp_mail.xml',
        'views/website_otp_views.xml',
        'templates/login.xml',
        'templates/signup.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'bi_website_otp_auth/static/src/js/login.js',
            'bi_website_otp_auth/static/src/scss/login.scss',
        ],
    },
    "license": 'OPL-1',
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/df5v2RGYsYc',
    "images":['static/description/Banner.gif'],
}
