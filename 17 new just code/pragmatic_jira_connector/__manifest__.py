{
    'name': 'Odoo Jira Connector',
    'version': '17.0.0',
    'author': 'Pragmatic TechSoft Pvt Ltd.',
    'website': 'http://www.pragtech.co.in',
    'category': 'Services',
    'summary': 'Synchronise data between Odoo and Jira odoo jira odoo connector jira connector odoo task bug jira task issue ',
    'description': """
    Odoo Jira Connector
    =======================================
    
    This connector will help user to import/export following objects in Jira.
    * Project
    * Task (Issues)
    * user
    * Attachments
    * Messages
    <keywords>
odoo jira odoo connector jira connector odoo task bug jira task issue
    """,
    'depends': ['project', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/project_views.xml',
        'views/res_company_views.xml',
        'wizards/message_view.xml'
    ],
    'images': ['image/Animated-Jira-connector.gif'],
    # 'images': ['static/description/end-of-year-sale-main.jpg'],
    'live_test_url': 'https://www.pragtech.co.in/company/proposal-form.html?id=103&name=odoo-jira-connector',
    'price': 99,
    'currency': 'EUR',
    'license': 'OPL-1',
    'auto_install': False,
    'application': False,
    'installable': True,
}
