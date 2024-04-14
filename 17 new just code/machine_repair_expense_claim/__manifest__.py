# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Machine Repair with Employee/User Expense Claim",
    'version': '6.1.5',
    'currency': 'EUR',
    'price': 45.0,
    'category' : 'Human Resources/Expenses',
    'license': 'Other proprietary',
    'summary': """Machine Repair Request Integration Employee/User Expense Claim.""",
    'description': """
machine repair
employee expense
hr expense
machine repair request
repair machine
repair product
product repair
expense claim
claim expense
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/mre.jpg'],
    #'live_test_url': 'https://youtu.be/POzAwt-rYx8',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/machine_repair_expense_claim/2',#'https://youtu.be/x5LXaiUx6TE',
    'depends': [
                'machine_repair_management',
                'hr_expense'
                ],
    'data':[
        'views/hr_expense_view.xml',
        'views/hr_expense_sheet_view.xml',
        'views/machine_repair_support.xml'
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
