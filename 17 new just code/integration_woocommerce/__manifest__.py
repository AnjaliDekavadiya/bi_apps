# See LICENSE file for full copyright and licensing details.

{
    'name': 'Odoo WooCommerce Connector PRO',
    'summary': "Export products and your current stock from Odoo,"
               " and get orders from WooCommerce."
               " Update order status and provide tracking numbers to your customers; "
               "All this automatically and instantly!",
    'category': 'Sales',
    'version': '17.0.1.6.1',
    'images': ['static/description/images/banner.gif'],
    'author': 'VentorTech',
    'website': 'https://ventor.tech',
    'support': 'support@ventor.tech',
    'license': 'OPL-1',
    'live_test_url': 'https://ventor.tech/contact-us/',
    'price': 449.00,
    'currency': 'EUR',
    'depends': [
        'integration',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/product_ecommerce_fields.xml',
        'wizard/import_customers_wizard_woocommerce.xml',
        'views/product_template_views.xml',
        'views/product_product_views.xml',
        'views/sale_integration.xml',
        'wizard/configuration_wizard_woocommerce.xml',
    ],
    'demo': [
    ],
    'external_dependencies': {
        'python': ['aiohttp'],
    },
    'installable': True,
    'application': True,
    "cloc_exclude": [
        "**/*"
    ]
}
