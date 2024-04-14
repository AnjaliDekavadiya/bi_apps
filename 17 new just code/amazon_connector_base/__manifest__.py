{
    'name': 'Amazon Connector - Odoo Enterprise FBM Extension',
    'version': '17.0.1.0.3',
    'category': 'Sales',
    'author': '4E Growth GmbH',
    'maintainer': 'Duc, DAO',
    'license': 'OPL-1',
    "website": "https://fouregrowth.com",
    "live_test_url":  "https://demo.fouregrowth.com/contactus",
    "description": """Amazon, Amazon Connector extension, Odoo 16 Amazon, Amazon Marketplace, Odoo native Amazon connector, Amazon FBA, Amazon FBM, Amazon Fulfilled by Merchant, Fulfillment by Amazon, Amazon Connector module, Amazon Deutschland, Amazon Germany, Amazon Canada, Amazon USA, Amazon Mexico, Amazon France, Amazon UK, Amazon Italy, Amazon Spain, Amazon EU, Amazon US, Amazon North America, sales order, SP API, Amazon MWS, Amazon vendor, Shopify, Woocommerce, Ebay, sendcloud, FBM, FBA, Amazon Module, Amazon API, Amazon SP API, Amazon odoo, Amazon Marketplace, Amazon Seller, Odoo Amazon connector, Odoo Amazon, Amazon Odoo Connector""",
    "summary": """Amazon, Amazon Connector extension, Odoo 16 Amazon, Amazon Marketplace, Odoo native Amazon connector, Amazon FBA, Amazon FBM, Amazon Fulfilled by Merchant, Fulfillment by Amazon, Amazon Connector module, Amazon Deutschland, Amazon Germany, Amazon Canada, Amazon USA, Amazon Mexico, Amazon France, Amazon UK, Amazon Italy, Amazon Spain, Amazon EU, Amazon US, Amazon North America, sales order, SP API, Amazon MWS, Amazon vendor, Shopify, Woocommerce, Ebay, sendcloud, FBM, FBA, Amazon Module, Amazon API, Amazon SP API, Amazon odoo, Amazon Marketplace, Amazon Seller, Odoo Amazon connector, Odoo Amazon, Amazon Odoo Connector""",
    'depends': [
        'sale_amazon',
        'delivery'
    ],
    'images': ['static/images/Amazon FBM Extension.gif'],
    'data': [
        # Data
        'data/ir_cron.xml',
        'data/ir_action_server_data.xml',
        'data/amazon_menus.xml',
        # Wizards
        'wizards/amazon_operation_wizard.xml',
        'wizards/generate_amazon_product_wizard.xml',
        # Views
        'views/amazon_account.xml',
        'views/amazon_offer_views.xml',
        'views/amazon_marketplace_views.xml',
        'views/amazon_report_log.xml',
        'views/amazon_report_type.xml',
        'views/amazon_synchronization_log.xml',
        # 'views/delivery_carrier_views.xml',
        'views/feed_submission_log.xml',
        'views/sale_order_views.xml',
        'views/product_product_views.xml',
        # Security
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'price': 299.00,
    'currency': 'EUR',
    'support': '4egrowth@gmail.com'
}
