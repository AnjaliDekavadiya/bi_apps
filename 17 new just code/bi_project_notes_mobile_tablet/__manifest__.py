# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Portal Project Notes- Notes on My Account Web Page',
    'version': '17.0.0.0',
    'category': 'Projects',
    'summary': 'Website Project Notes on website Project portal notes on website note for projects note on website my account project notes on mobile project notes on tablet view notes on web my account project notes on portal view note on portal  mobile view notes',
    'description': """
        This plug-in helps to manage Project Notes Mobile Tablet
		modify notes
		edit notes on project 
		edit notes from mobile
		notes on mobile
		notes account
		notes portal
		note in system
		
		
    """,
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.com',
    'price': 9,
    'currency': 'EUR',
    'depends': [
        'web', 'portal', 'website','website_forum',
         'sale_management', 'purchase','web_editor','website_profile',
        'stock', 'hr', 'project',
        'bi_odoo_job_costing_management', 'bi_material_purchase_requisitions'],
    'data': [
        'views/project_note_templaes.xml',
    ],
    'qweb': [
    ],

    'assets': {
        'web.assets_frontend': [
            "bi_project_notes_mobile_tablet/static/src/js/project_task.js",
        ],
    },

    'auto_install': False,
    'installable': True,
    'license': 'OPL-1',
    'live_test_url': 'https://youtu.be/qRomYQKqBWw',
    'images': ['static/description/Banner.gif'],
}

