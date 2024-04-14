# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Budget Forecasting',
    'version': '17.0',
    'price': 279,
    'currency': 'EUR',
    'category': 'Accounting/Accounting',
    'summary': """ 
          
        """,
    'description': """
        
    """,
    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',
    'images': [],
    'depends': ['setu_cash_flow_forecasting', 'account_budget'],
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'license': 'OPL-1',
    'sequence': 20,
    'data': [
        'security/ir.model.access.csv',
        'views/crossovered_budget.xml',
        'views/setu_cash_forecast_type.xml',
        'views/account_budget_post.xml',
        'wizard/budget_comparison_wizard.xml',
        'views/budget_menus.xml',
        'views/fiscal_period.xml',
        'views/setu_budget_forecast_settings.xml'
    ],
    'assets': {
        'web.assets_backend': [
                'setu_budget_forecasting/static/src/js/lib/apexcharts.min.js',
                'setu_budget_forecasting/static/src/js/setu_budget_forecasting_dashboard.js',
                'setu_budget_forecasting/static/src/xml/**/*',
            ],
    },
    'application': True,
    # 'post_init_hook': 'create_cash_forecast_type',
    'live_test_url' : 'https://www.youtube.com/playlist?list=PLH6xCEY0yCIB-k1yPvSZHhZEsqVYE0evq',
}
