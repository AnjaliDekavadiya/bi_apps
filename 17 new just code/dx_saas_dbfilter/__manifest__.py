# -*- coding: utf-8 -*-
{
    'name': "Simple SAAS",
    'summary': """
    This module allows you to sell odoo as service (SAAS) just like odoo online This module uses odoo dbfilter configuration wich allows you to host many database on
        the same odoo installation without seeing each other 
        """,
    'description': """
    This module allows you to sell odoo as service (SAAS) just like odoo online This module uses odoo dbfilter configuration wich allows you to host many database on
    the same odoo installation without seeing each other 
    """,
    'author': "SADEEM | DXEG",
    'website': "https://sadeem.cloud",
    'category': 'Technical',
    'version': '17.240202',
    'depends': ['account', 'product', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/sequence.xml',
        'wizard/download_backup_format_views.xml',
        'views/res_config_views.xml',
        'views/template.xml',
        'views/product_template.xml',
        'views/supscriptions_view.xml',
        'views/servers_view.xml',
        'views/odoo_versions_views.xml',
        'views/packages_views.xml',
        'views/modules_views.xml',
        'views/menus.xml',
        'views/portal_views.xml',
    ],
    'images': ['static/description/images/banner.gif'],
    'price': 300.00,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'live_test_url': 'https://youtu.be/2CAmw0zfzj4',
    'license': 'OPL-1',
    'application': True,
}
