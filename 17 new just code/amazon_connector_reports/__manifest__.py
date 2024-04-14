{
    'name': 'Amazon Connector - All Reports Extension',
    'version': '17.0.1.0.1',
    'category': 'Sales',
    'author': '4E Growth GmbH',
    'maintainer': 'Duc, DAO',
    'license': 'OPL-1',
    "website": "https://fouregrowth.com",
    "live_test_url":  "https://demo.fouregrowth.com/contactus",
    "description": """Amazon report, Amazon reports, settlement report, reconciliation report, tax report, inventory report, Fulfillment by Amazon report, compliance report, business reports, performance reports, Amazon retail analytics report, analytics report, return reports, Amazon FBA, Amazon BI, Amazon API, Amazon Marketing, AMAZON data analytics, Amazon invoice data""",
    "summary": """Amazon report, Amazon reports, settlement report, reconciliation report, tax report, inventory report, Fulfillment by Amazon report, compliance report, business reports, performance reports, Amazon retail analytics report, analytics report, return reports, Amazon FBA, Amazon BI, Amazon API, Amazon Marketing, AMAZON data analytics, Amazon invoice data""",
    'depends': [
        'amazon_connector_base',
        'documents',
    ],
    'images': ['static/images/Amazon Reports Extension.gif'],
    'data': [
        # Data
        'data/amazon_report_type_data.xml',
        # Wizards
        'wizards/report_choose_marketplace_wizard.xml',
        # Views
        'views/amazon_report_log.xml',
        'views/amazon_report_type.xml',
        # Security
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'price': 399.00,
    'currency': 'EUR',
    'support': '4egrowth@gmail.com'
}
