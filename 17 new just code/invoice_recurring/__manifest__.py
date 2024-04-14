# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Recurring Invoice',
    'version': '1.0',
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'https://www.synconics.com',
    'sequence': 15,
    'category': 'Accounting',
    'summary': 'Allows to create recurring invoice',
    'description': """
Create recurring invoices.
==========================
* This application allows to create recurring invoice.
    """,
    'depends': ['account'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'data/mail_template.xml',
        'data/subscription_demo.xml',
        'view/subscription_view.xml',
        'view/menu.xml',
    ],
    'demo': [],
    'images': ['static/description/main_screen.png'],
    'price': 35.00,
    'currency': 'EUR',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
}
