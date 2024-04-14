# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full
# copyright and licensing details.

{
    'name': 'Analytic Account Profit and Loss Report',
    'version': '7.1.2',
    'price': 59.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category': 'Invoices & Payments',
    'summary': 'Print Profit and Loss report for selected Analytic Accounts / Project.',
    'description': """
odoo
project profit and loss
profit and loss project
analytic account profit and loss
analytic profit and loss
profit and loss report odoo
project management profit and loss
p&l
Project / Analytic Account Profit and Loss Report
""",
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    'live_test_url' : 'https://probuseappdemo.com/probuse_apps/project_profit_loss_report/347',#'https://youtu.be/SFZ67O6GNds',
    'depends': [
        'analytic',
        #'hr',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'report/report_project_profit_loss.xml',
        'wizard/project_profit_loss_view.xml',
    ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
