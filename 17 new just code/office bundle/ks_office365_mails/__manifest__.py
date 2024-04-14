{
    "name": "Odoo Office365 Mails",

    "summary": """
        Integrate Odoo Office 365 to streamline all of your office operations and business procedures effectively and simply. Work with Office 365 applications while reaping the benefits of smart integration. Odoo Office 365 Connectors, Office 365 Connectors, Odoo Office 365 Connector, Odoo Office365 Connector, Office 365, Odoo Office 365, Odoo Integration, API Office 365 Task, Office 365 Mail, Office 365 Contact, Office 365 Calendar, All In One Office 365, Odoo and Office365, Sync Calendar, Sync Contact, API Office 365, Office 365 Task, Office365, Microsoft Office 365, Odoo ERP, Microsoft SSO, Odoo Office 365, Microsoft Integration, Contact Synchronization, Office 365 Synchronization.
    """,

    "description": """
            Office365 Inbox Sync Apps
            Office365 Mails Apps
            Office365 Sent Item Syncing Apps
            Office365 Archive syncing Apps
            Mail Messages Sync Apps
            Auto refresh Mail Sync Apps
            Detailed Log mail sync
            User Specific Syncing
            Cron Job Syncing
            Automatic Mails Syncing
            Mails Attachment syncing 
            Office365 Mails
            Folderwise syncing Apps
            365 Apps
            Odoo Office 365 Apps
            Office 365 Apps
            Odoo 365 connector Apps
            Office 365 Mails Apps
            Office 365 connector Apps
            Office 365 Mails sync
            Office 365 Outlook sync Apps
            Office 365 Outlook connector Apps
            Microsoft Office 365 Mails
            Manual sync Apps
            Two-Way Odoo Apps
            Two-Way Mails sync Apps
            Mails Syncing Apps
            Two-Way Syncing Apps
            Mails Connector
            Microsoft 365 Mails Apps
            Microsoft 365 connector Apps
            Best Office 365 Apps
            Top Office 365 Apps
            Best Microsoft 365 Apps
            Best Mails Syncing Apps
            Best Connector Apps
            Best Outlook Syncing Apps
            Office 365 Add on
            Outlook Mails sync
            Odoo Outlook Add on
            Sync Outlook to Odoo
            Two-Way Apps
            Best Two-Way Sync Apps
            Automatic Two-Way sync
    """,

    'author': "Ksolves India Ltd.",
    'license': 'OPL-1',
    'currency': 'EUR',
    'price': 100,
    'website': "https://store.ksolves.com/",
    'maintainer': 'Ksolves India Ltd.',
    'category': 'Tools',
    'version': '17.0.1.0.0',
    'support': 'sales@ksolves.com',
    'live_test_url': 'https://office365demo14.kappso.com/web/demo_login',

    "depends": ['base',
                'mail',
                "ks_office365_base",
                ],

    "data": [
        'security/ir.model.access.csv',
        'security/ks_user_record_rules.xml',
        'views/ks_mail_category.xml',
        'views/ks_office365_mails_user_form.xml',
        'views/ks_office_mail_jobs.xml',
        'data/ks_mail_cron.xml',
    ],

    "images": [

        "static/description/Office365_Mails_v17.gif",

    ],

    'assets': {
        'web.assets_backend': [
            'ks_office365_mails/static/src/js/ks_message.js',
            'ks_office365_mails/static/src/xml/composer.xml'
        ],
        'web.assets_qweb': [
            'ks_office365_mails/static/src/xml/ks_thread.xml',
        ],
    },

    'uninstall_hook': 'uninstall_hook',
}
