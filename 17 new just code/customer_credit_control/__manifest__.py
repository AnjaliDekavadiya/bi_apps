{
    'name': "Customer Credit Control",
    'version': '1.0',
    'depends': ['sale_management'],
    'author': "Aakash Infosoft",
    'website': "https://aakash.com",
    'category': 'Sale Management',
    'summary': "Manage your customer's credit due amount, dueation and send warning emails if needed.",
    'license': "OPL-1",
    'description': """
    This app is useful to configure credit control for each customer.
    """,
    'data': [
        "data/ir_cron.xml",
        "views/res_partner_views.xml",
        "views/warning_mail_views.xml",
        "views/sales_views.xml",
        "wizard/res_config_settings_views.xml",
        "security/ir.model.access.csv"
    ],
    'images': [
        'static/description/ccc.jpg',
    ],
    'price': 49.99,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
    'application': True,
}