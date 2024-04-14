# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Expenses Portal for Customer",
    'version': '7.1.3',
    'price': 49.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category': 'Human Resources/Expenses',
    'summary': """Allow your customers to view expenses on portal of your website.""",
    'description': """
Expense Customer Portal

    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': 'www.probuse.com',
    'images': ['static/description/Expenses.jpg'],
    #'live_test_url': 'https://youtu.be/jDLyy1nkEAE',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/expense_customer_portal/483',#'https://youtu.be/LMaP1jAcHZg',
    'depends': [
        'hr_expense',
        'portal',
    ],

    'data': [
        'views/hr_expense_view.xml',
        'views/expense_template.xml',
    ],

    'installable': True,
    'application': False,
}
