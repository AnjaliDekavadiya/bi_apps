{
    'name': 'Whatsapp Chatbot',
    'version': '17.0.0',
    'version': '17.0',
    'category': 'Services',
    'author': 'Pragmatic TechSoft Pvt Ltd.',
    'website': 'pragtech.co.in',
    'summary': 'IVR Chatbot Interactive voice response text response helpdesk business automation automatic response whatsapp chatbot chat bot chat-bot multivendor  automatic ticket automatic FAQ automatic customer feedback customer response whatsapp business live chat',
    'description': "IVR Chatbot Interactive voice response text response helpdesk business automation automatic response whatsapp chatbot chat bot chat-bot multivendor  automatic ticket automatic FAQ automatic customer feedback customer response whatsapp business live chat",
    'depends': ['base_setup', 'pragtech_whatsapp_base', 'hr', 'web_hierarchy'],
    'data': [
        'security/ir.model.access.csv',
        'views/whatsapp_helpdesk_messages_view.xml',
        'views/res_config_settings_view.xml',
        'views/whatsapp_messages_history_view.xml',
        # 'views/wh_templates.xml',
        'wizard/scan_whatsapp_views.xml',
    ],

    'assets': {
        'web._assets_primary_variables': [
            'pragtech_whatsapp_central/static/src/scss/variables.scss',
        ],
        'web.assets_backend': [
            'pragtech_whatsapp_central/static/src/js/pragtech_whatsapp_central.js',
            'pragtech_whatsapp_central/static/src/xml/pragtech_whatsapp_central.xml',
            'pragtech_whatsapp_central/static/src/scss/pragtech_whatsapp_central.scss',
        ],
        'web.assets_qweb': [
        ],
    },
    'images': ['static/description/whatsapp_chatbot_gupshup.gif'],
    'live_test_url': 'https://www.pragtech.co.in/company/proposal-form.html?id=103&name=odoo-whatsapp-ivr',
    'price': 249,
    'currency': 'USD',
    'license': 'OPL-1',
    'application': False,
    'auto_install': False,
    'installable': True,
}
