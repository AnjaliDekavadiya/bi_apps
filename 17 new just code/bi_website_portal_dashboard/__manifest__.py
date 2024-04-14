# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "Dashboard for Portal Users",
    "version" : "17.0.0.0",
    "category" : "Website",
    'summary': 'Portal Attractive website dashboard portal analysis chart  portal dashboard view portal pie chart portal dashboard portal user dashboard website portal dashboard portal analysis dashboard for portal login user portal chart dashboard portal user chart view',
    "description": """
    
        This odoo app helps user to show attractive website dashboard, user can see different records with couns and different analysis chart for sales , purchase, invoice, bills, sold products and purchased products, also can see latest quotations, sales orders, RFQs, and purchase orders, invoices and bills with status and projects and task from portal view, Also can filter all charts by today, week, month, year.
    
    """,
    "author": "BrowseInfo",
    "website" : "https://www.browseinfo.com",
    "price": 49,
    "currency": 'EUR',
    "depends" : ['website','base','sale','website_crm_partner_assign'],
    "data": [
        'security/ir.model.access.csv',
        'views/website_portal_dashboard_templates.xml',
        'views/res_config_settings_inherit_views.xml',
        'views/res_partner_inherit_views.xml',
        
    ],
    "qweb" : [],
    'assets': {
    'web.assets_frontend': [
            'bi_website_portal_dashboard/static/src/scss/website_portal_dashboard.scss',
            'bi_website_portal_dashboard/static/src/js/website_portal_dashboard.js',
        ],
    },
    'license': 'OPL-1',
    "auto_install": False,
    "installable": True,
    "live_test_url":'https://youtu.be/PT37ebRCUF4',
    "images":["static/description/Banner.gif"],
}
