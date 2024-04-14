# -*- coding: utf-8 -*-
{
    'name': "mana_dashboard_search",

    'summary': """
        search for mana dashboard
       """,

    'description': """
        search for mana dashboard
    """,

    'author': "crax",
    'website': "https://www.openerpnext.com",

    'category': 'Apps/Dashboard',
    'version': '17.0.0.1',
    'price': 199.00,
    'license': 'OPL-1',

    'depends': ['base', 'web', 'mana_dashboard_base'],
    'images': ['static/description/banner.png'],

    'data': [],

    'assets': {
        'web.assets_backend': [
            
            # record selector
            "/mana_dashboard_search/static/src/many2x_wrapper/mana_record_selector.js",
            "/mana_dashboard_search/static/src/many2x_wrapper/mana_record_selector.xml",

            # search
            "/mana_dashboard_search/static/src/search/mana_search_group.js",
            "/mana_dashboard_search/static/src/search/mana_search_item.js",
            "/mana_dashboard_search/static/src/search/mana_search_many2many.js",
            "/mana_dashboard_search/static/src/search/mana_search_button.js",
            "/mana_dashboard_search/static/src/search/mana_search_input.js",
            "/mana_dashboard_search/static/src/search/mana_search_many2one.js",
            "/mana_dashboard_search/static/src/search/mana_search_tab.js",
            "/mana_dashboard_search/static/src/search/mana_search_select.js",
            "/mana_dashboard_search/static/src/search/mana_search_time_range.js",
            "/mana_dashboard_search/static/src/search/mana_search_option.js",
        ]
    }
}
