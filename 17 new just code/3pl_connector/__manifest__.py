# -*- coding: utf-8 -*-

{
    'name': 'Odoo - 3PL Connector',
    'version': '17.0.1.0',
    'summary': 'Odoo - 3PL Connector through FTP/SFTP\
    FTP\
    SFTP\
    FTP/SFTP\
    SFTP/FTP',
    'category': 'Sales',
    'sequence': 1,
    'live_test_url': 'https://youtu.be/iymu6zii5UU',
    'description': """
Odoo - 3PL connector to import - export data and process pickings through FTP/SFTP.
    FTP
    SFTP
    FTP/SFTP
    SFTP/FTP
    """,
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'depends': ['stock_delivery'],
    'demo': [
    ],
    'data': [
        "data/ir_sequence.xml",
        "data/email_templates.xml",
        "data/ir_cron.xml",
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        "views/ftp_server_view.xml",
        "views/stock_view.xml",
        "views/process_log_view.xml",
        "views/stock_picking_view.xml",
        "wizard/tpl_operations_view.xml",
        "wizard/ftp_test_connection_wizard_view.xml",
        "views/menuitems.xml"
    ],
    'external_dependencies': {
        'python': ['xlrd', 'pysftp', 'ftplib'],
    },
    'images': [
        'static/description/main_screen.png'
    ],
    'price': 150.00,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}
