# Copyright 2020 VentorTech OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

{
    'name': 'Odoo QuickBooks Online Connector PRO',
    'summary': '''
        Sync Invoices, Payments, Taxes, between Odoo and QuickBooks Online (Intuit)
        automatically or manually
    ''',
    'version': '17.0.1.2.4',
    'category': 'Accounting',
    'author': 'VentorTech',
    'website': 'https://ventor.tech',
    'support': 'support@ventor.tech',
    'license': 'OPL-1',
    'live_test_url': 'https://ventor.tech/contact-us/',
    'price': 199.00,
    'currency': 'EUR',
    'depends': [
        'sale_management',
        'sale_purchase',
        'account',
        'stock_dropshipping',
        'queue_job',
    ],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',
        # Wizard views
        'wizard/qbo_help_wizard_views.xml',
        # Mapping views
        'views/mapping/qbo_map_mixin_views.xml',
        'views/mapping/qbo_map_account_move_views.xml',
        'views/mapping/qbo_map_partner_views.xml',
        'views/mapping/qbo_map_product_views.xml',
        'views/mapping/qbo_map_account_views.xml',
        'views/mapping/qbo_map_tax_views.xml',
        'views/mapping/qbo_map_taxcode_views.xml',
        'views/mapping/qbo_map_term_views.xml',
        'views/mapping/qbo_map_payment_method_views.xml',
        'views/mapping/qbo_map_payment_views.xml',
        'views/mapping/qbo_map_sale_order_views.xml',
        'views/mapping/qbo_map_department_views.xml',
        # Standard views
        'views/res_config_settings_views.xml',
        'views/product_views.xml',
        'views/product_category_views.xml',
        'views/res_partner_views.xml',
        'views/account_move_views.xml',
        'views/account_payment_views.xml',
        'views/sale_order_views.xml',
        'views/stock_warehouse_views.xml',
        'views/ir_action.xml',
        'views/ir_menu.xml',
        # Data
        'data/ir_cron.xml',
        'data/res_company.xml',
        'data/mail_template.xml',
        'data/queue_data.xml',
    ],
    'external_dependencies': {
        'python': [
            'python-quickbooks',
            'intuit-oauth',
            'pycountry',
            'future',
        ],
    },
    'images': [
        "static/description/banner.gif",
    ],
    "cloc_exclude": [
        "**/*",
    ],
    'installable': True,
    'application': True,
}
