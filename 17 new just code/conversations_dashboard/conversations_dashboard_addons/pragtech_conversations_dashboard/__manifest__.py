{
    'name': 'Conversations Dashboard',
    'version': '17.0.0.1',
    'summary': 'Conversations Dashboard system',
    'description': 'Conversations Dashboard system',
    'depends': ['base', 'mail', 'base_setup', 'bus', 'web_tour', 'product', 'purchase', 'sale'],
    'data': [
            #  'views/assets.xml',
             'views/resconfig.xml',
             'views/pragtech_conversations_dashboard.xml',
             'views/mail_channel_views.xml',
             'security/ir.model.access.csv',
             ],
    'assets': {
        # Custom bundle in case we want to remove things that are later added to web.assets_common
        'mail.assets_common_discuss_public': [
            ('include', 'web.assets_common'),
        ],
        'web.assets_backend': [
            'web/static/src/legacy/utils.js',
            'web/static/src/legacy/js/core/widget.js',
            'web/static/src/legacy/js/core/class.js',
            'web/static/src/legacy/js/core/mixins.js',
            'web/static/src/legacy/js/core/service_mixins.js',
            'web/static/src/legacy/js/core/dom.js',
            'web/static/src/legacy/js/public/public_widget.js',
        #     'pragmatic_odoo_whatsapp_integration/static/src/xml/*.xml',
            'pragtech_conversations_dashboard/static/src/xml/whatsapp_widget.xml',
            'pragtech_conversations_dashboard/static/src/xml/Internal_records.xml',
            'pragtech_conversations_dashboard/static/src/xml/whatsapp_sidebar.xml',
            'pragtech_conversations_dashboard/static/src/xml/thread.xml',
            'pragtech_conversations_dashboard/static/src/xml/attachment_list.xml',
            'pragtech_conversations_dashboard/static/src/xml/whatsapp_message.xml',
            'pragtech_conversations_dashboard/static/src/xml/whatsapp_composer.xml',
            'pragtech_conversations_dashboard/static/src/xml/autoresize_input.xml',
            'pragtech_conversations_dashboard/static/src/xml/whatsapp_thread_icon.xml',
            'pragtech_conversations_dashboard/static/src/xml/message_seen_indicator17.xml',
            'pragtech_conversations_dashboard/static/src/xml/whatsapp_sidebar_categories.xml',
            'pragtech_conversations_dashboard/static/src/xml/client_action.xml',
            # 'pragtech_conversations_dashboard/static/src/xml/*.xml',

            'pragtech_conversations_dashboard/static/src/dashboard_v17/discuss_app_model_patch.js',
            'pragtech_conversations_dashboard/static/src/dashboard_v17/thread_model_patch.js',
            'pragtech_conversations_dashboard/static/src/dashboard_v17/message_model_patch.js',
            'pragtech_conversations_dashboard/static/src/dashboard_v17/whatsapp_widget.js',
            'pragtech_conversations_dashboard/static/src/dashboard_v17/internal_records.js',
            'pragtech_conversations_dashboard/static/src/dashboard_v17/whatsapp_sidebar.js',
            'pragtech_conversations_dashboard/static/src/dashboard_v17/whatsapp_message.js',
            'pragtech_conversations_dashboard/static/src/dashboard_v17/whatsapp_composer.js',
            'pragtech_conversations_dashboard/static/src/dashboard_v17/autoresize_input.js',
            'pragtech_conversations_dashboard/static/src/dashboard_v17/thread.js',
            'pragtech_conversations_dashboard/static/src/dashboard_v17/whatsapp_thread_icon.js',
            'pragtech_conversations_dashboard/static/src/dashboard_v17/message_seen_indicator.js',
            'pragtech_conversations_dashboard/static/src/dashboard_v17/whatsapp_sidebar_categories.js',
            'pragtech_conversations_dashboard/static/src/dashboard_v17/client_action.js',
            'pragtech_conversations_dashboard/static/src/dashboard_v17/messaging_service.js',
            'pragtech_conversations_dashboard/static/src/dashboard_v17/messaging_service_patch.js',
            # 'pragtech_conversations_dashboard/static/src/discuss_sidebar_category_item/discuss_sidebar_category_item.js',
            'pragtech_conversations_dashboard/static/src/css/*.scss',
            # 'pragtech_conversations_dashboard/static/src/list_renderer/contactView.js',
            # 'pragtech_conversations_dashboard/static/src/list_renderer/salesView.js',
            # 'pragtech_conversations_dashboard/static/src/list_renderer/purchaseView.js',
            # 'pragtech_conversations_dashboard/static/src/list_renderer/invoicingView.js',
            # 'pragtech_conversations_dashboard/static/src/composer/composer.js',
            # 'pragtech_conversations_dashboard/static/src/composer_text_input/composer_text_input.js',
            # 'pragtech_conversations_dashboard/static/src/list_renderer/list_renderer.js',
            # 'pragtech_conversations_dashboard/static/src/list_renderer/list_controller.js',
            # 'pragtech_conversations_dashboard/static/src/list_renderer/list_view.js',
            # 'pragtech_conversations_dashboard/static/src/thread_view/thread_view.js',
            # 'pragtech_conversations_dashboard/static/src/discuss_sidebar_item/discuss_sidebar_item.js',
            # 'pragtech_conversations_dashboard/static/src/js/discuss_extend/sidebar.js',
            # 'pragtech_conversations_dashboard/static/src/models/messaging_initializer/messaging_initializer.js',
            # 'pragtech_conversations_dashboard/static/src/discuss_widget/discuss_widget.xml',
            # 'pragtech_conversations_dashboard/static/src/js/discuss_extend/discuss_component.xml',
            # 'pragtech_conversations_dashboard/static/src/**/*.css',
            # 'pragtech_conversations_dashboard/static/src/**/*.scss'
        ],
        'web.assets_common': [
            'pragtech_conversations_dashboard/static/lib/js/spectrum.js',
            'pragtech_conversations_dashboard/static/lib/js/apexcharts.min.js',
            'pragtech_conversations_dashboard/static/lib/js/bootstrap-iconpicker.min.js',
            'pragtech_conversations_dashboard/static/lib/js/jquery.ui.touch-punch.min.js',
            'pragtech_conversations_dashboard/static/lib/js/gridstack.min.js',
            'pragtech_conversations_dashboard/static/lib/js/gridstack.jQueryUI.min.js',
            'pragtech_conversations_dashboard/static/lib/css/spectrum.css',
            'pragtech_conversations_dashboard/static/lib/css/bootstrap-iconpicker.min.css',
            'pragtech_conversations_dashboard/static/lib/css/gridstack.min.css',
            'pragtech_conversations_dashboard/static/lib/css/apexcharts.css',
        ],
    },
    
    'jquery': True,
    'bootstrap': True,
    'installable': True,
    'auto-install': False,
    'application': True,
}