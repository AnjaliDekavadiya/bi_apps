# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Sales Commission on Agent by ID Search",
    'version': '9.1.2',
    'price': 330.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category': 'Sales/Sales',
    'summary': """Sales Agent Search by ID and Add on Website Order""",
    'description': """
Users Unique Number Odoo
user number
user sequence number
user unique number
Users Unique Sequence Number Odoo
Internal Users Unique Number
Portal Users Unique Number
Sales Commission on Agent by ID Search
Sales Agent Search by ID and Add on Website Order
    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/image.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/sales_commission_agent_uniqueid/81',#'https://youtu.be/a-GDTIbO3qY',
    'depends': [
#        'base',
        'sales_agent_representative_shop',
        'sales_commission_external_agent_portal',
        'sales_commission_external_user',
    ],

    'data': [
        'data/user_sequence.xml',
#        'views/res_partner_view.xml',
        'views/res_config_setting_view.xml',
        'views/res_users_view.xml',
        'views/payment_templates.xml',
    ],
    'installable': True,
    'application': False,
    
}
