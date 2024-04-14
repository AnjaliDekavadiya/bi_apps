# -*- coding: utf-8 -*-
{
    'name': "akl_multi_tab_plugin",

    'summary': """
        akl multi tab plugin for odoo""",

    'description': """
        akl multi tab plugin
        multi tab,
        multi tab theme,
        odoo theme
    """,

    'author': 'funenc odoo',
    'website': 'https://www.openerpnext.com',
    'live_test_url': 'https://www.openerpnext.com',

    'category': 'Backend/Theme',
    'version': '17.0.0.1',
    'license': 'OPL-1',
    'images': ['static/description/banner.png',
               'static/description/akl_screenshot.png'],

    'depends': ['base','web'],

    "application": False,
    "installable": True,
    "auto_install": False,

    'price': 129,
    'currency': 'USD',
    
    'data': [],

    'assets': {
        'web.assets_backend': [
    
            'akl_multi_tab_plugin/static/src/components/multi_tab/akl_multi_tab.scss',
            'akl_multi_tab_plugin/static/src/components/multi_tab/akl_multi_tab.js',
            'akl_multi_tab_plugin/static/src/components/multi_tab/akl_multi_tab.xml',
            
            'akl_multi_tab_plugin/static/src/akl_action_container.js',
            'akl_multi_tab_plugin/static/src/akl_action_service.js',
            'akl_multi_tab_plugin/static/src/akl_list_patch.js',
        ]
    }
}
