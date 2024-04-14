# -*- coding: utf-8 -*-
{
    'name': "mana_dashboard_base",

    'summary': """
        Base module for mana_dashboard
     """,

    'description': """
        Base module for mana_dashboard 
    """,

    'author': "crax",
    'website': "https://www.openerpnext.com",

    'category': 'Apps/Dashboard',
    'version': '17.0.0.8',
    'license': 'OPL-1',

    'depends': ['base', 'web'],
    'images': ['static/description/banner.png'],

    'data': [
        'security/ir.model.access.csv',
        
        'views/mana_template.xml',
        'views/mana_dashboard_template.xml',
        'views/mana_result_type.xml',
        'views/mana_data_source_type.xml',
        'views/mana_series_type.xml',

        'data/mana_data_source_type.xml',
        'data/mana_result_type.xml'
    ],

    'assets': {
        'web.assets_backend': [
            "/mana_dashboard_base/static/src/template_component/*.js",

            "/mana_dashboard_base/static/src/charts/mana_chart_util.js",
            "/mana_dashboard_base/static/src/charts/mana_chart_builder.js",

            "/mana_dashboard_base/static/src/mana_block_base.js",
            "/mana_dashboard_base/static/src/mana_block_registry.js",

            # data source
            "/mana_dashboard_base/static/src/data_source/mana_data_source.js",
            "/mana_dashboard_base/static/src/data_source/mana_record.js",
            "/mana_dashboard_base/static/src/data_source/mana_config.js",

            # libs
            "/mana_dashboard_base/static/libs/moment/moment.min.js",
            "/mana_dashboard_base/static/libs/underscore/underscore.min.js",
            "/mana_dashboard_base/static/libs/editor/editor.min.js",
            "/mana_dashboard_base/static/libs/editor/editor.min.css",
            "/mana_dashboard_base/static/libs/echarts/echarts.min.js",
            "/mana_dashboard_base/static/libs/select2/select2.min.js",
            "/mana_dashboard_base/static/libs/select2/select2.min.css",
            
            # many2x wrapper
            "/mana_dashboard_base/static/src/many2x_wrapper/mana_many2x_wrapper.js",
            "/mana_dashboard_base/static/src/many2x_wrapper/mana_many2x_wrapper.xml",

            # resize
            "/mana_dashboard_base/static/libs/ResizeObserver/ResizeObserver.js",
            "/mana_dashboard_base/static/src/resize_manager/resize_manager.js",

            # block icon
            "/mana_dashboard_base/static/src/utils/mana_icons.js",

            # qweb block
            "/mana_dashboard_base/static/src/qweb_block/qweb_block.js",

            "/mana_dashboard_base/static/xml/misc.xml"
        ]
    }
}
