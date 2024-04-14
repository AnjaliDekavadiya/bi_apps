{
    'name': 'Amazon Connector - Fulfillment by Amazon',
    'version': '17.0.1.0.1',
    'category': 'Sales',
    'author': '4E Growth GmbH',
    'maintainer': 'Duc, DAO',
    'license': 'OPL-1',
    "website": "https://fouregrowth.com",
    "live_test_url":  "https://demo.fouregrowth.com/contactus",
    "description": """Amazon connector, Amazon FBA, Amazon API, Odoo 16 Amazon, Amazon Marketplace, Odoo native Amazon connector, Amazon FBA, Amazon FBM, Amazon Fulfilled by Merchant, Fulfillment by Amazon, Amazon Connector module, Amazon Seller, Amazon plugin, Amazon App, Amazon Deutschland, Amazon Germany, Amazon Canada, Amazon USA, Amazon Mexico, Amazon France, Amazon UK, Amazon Italy, Amazon Spain, Amazon EU, Amazon US, Amazon North America, sales order, SP API, Amazon MWS, Amazon vendor, sendcloud, FBM, FBA, Amazon Module, Amazon API, Amazon SP API, Amazon odoo, Amazon Marketplace, Amazon Seller, Odoo Amazon connector, Odoo Amazon, Amazon Odoo Connector""",
    "summary": """Amazon connector, Amazon FBA, Amazon API, Odoo 16 Amazon, Amazon Marketplace, Odoo native Amazon connector, Amazon FBA, Amazon FBM, Amazon Fulfilled by Merchant, Fulfillment by Amazon, Amazon Connector module, Amazon Seller, Amazon plugin, Amazon App, Amazon Deutschland, Amazon Germany, Amazon Canada, Amazon USA, Amazon Mexico, Amazon France, Amazon UK, Amazon Italy, Amazon Spain, Amazon EU, Amazon US, Amazon North America, sales order, SP API, Amazon MWS, Amazon vendor, sendcloud, FBM, FBA, Amazon Module, Amazon API, Amazon SP API, Amazon odoo, Amazon Marketplace, Amazon Seller, Odoo Amazon connector, Odoo Amazon, Amazon Odoo Connector""",
    'depends': [
        'amazon_connector_base',
        'helpdesk',
    ],
    'images': ['static/images/Amazon FBA Extension.gif'],
    'data': [
        # Data
        'data/amazon_fulfillment_center_data.xml',
        'data/amazon_report_type_data.xml',
        # Wizards
        'wizards/amazon_operation_wizard.xml',
        'wizards/amazon_outbound_order_wizard.xml',
        # Views
        'views/account_fiscal_position_views.xml',
        'views/amazon_fulfillment_center_views.xml',
        'views/amazon_marketplace_views.xml',
        'views/amazon_report_log.xml',
        'views/amazon_report_type.xml',
        'views/sale_order_views.xml',
        'views/stock_warehouse_views.xml',
        # Security
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'price': 200.00,
    'currency': 'EUR',
    'support': '4egrowth@gmail.com'
}
