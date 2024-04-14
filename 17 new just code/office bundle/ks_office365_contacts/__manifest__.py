# -*- coding: utf-8 -*-
{
	'name': 'Office365 Contacts',

	'summary': """
Integrate Odoo Office 365 to streamline all of your office operations and business procedures effectively and simply. Work with Office 365 applications while reaping the benefits of smart integration. Odoo Office 365 Connectors, Office 365 Connectors, Odoo Office 365 Connector, Odoo Office365 Connector, Office 365, Odoo Office 365, Odoo Integration, API Office 365 Task, Office 365 Mail, Office 365 Contact, Office 365 Calendar, All In One Office 365, Odoo and Office365, Sync Calendar, Sync Contact, API Office 365, Office 365 Task, Office365, Microsoft Office 365, Odoo ERP, Microsoft SSO, Odoo Office 365, Microsoft Integration, Contact Synchronization, Office 365 Synchronization.
""",

	'description': """
365 Apps
        Odoo Office 365 Apps
        Office 365 Apps
        Odoo 365 connector Apps
        Office 365 contacts Apps
        Office 365 connector Apps
        Office 365 contact sync
        Office 365 people sync Apps
        Office 365 people connector Apps
        Microsoft Office 365 connector
        Manual sync Apps
        Two Way Odoo Apps
        Two Way Contact sync Apps
        Contact Syncing Apps
        Two-Way Syncing Apps
        Contact Connector
        Microsoft 365 Contact Apps
        Microsoft 365 connector Apps
        Best Office 365 Apps
        Top Office 365 Apps
        Best Microsoft 365 Apps
        Best Contact Syncing Apps
        Best Connector Apps
        Best People Syncing Apps
        Office 365 Add In
        Outlook contacts sync
        Best Two Way Sync Apps
        Automatic two-way sync
        Odoo Outlook Add-In
        Two-Way Apps
        Sync Apps
""",

	'author': 'Ksolves India Ltd.',

	'license': 'OPL-1',

	'currency': 'EUR',

	'price': '75',

	'website': 'https://store.ksolves.com/',

	'maintainer': 'Ksolves India Ltd.',

	'category': 'Tools',

	'version': '17.0.1.0.0',

	'support': 'sales@ksolves.com',

	'live_test_url': 'https://office365demo15.kappso.com/',

	'depends': ['base', 'ks_office365_base'],

	'data': ['security/ir.model.access.csv', 'views/ks_contacts.xml', 'data/ks_contact_cron.xml'],

	'assets': {'web.assets_backend': []},

	'images': ['static/description/Ks_Office365_Contacts_V17.gif'],


	'post_init_hook': 'install_hook',
}
