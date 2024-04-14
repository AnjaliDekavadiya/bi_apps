# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Submit Expenses for Helpdesk Tickets",
    'version': '4.5.2',
    'price': 9.0,
    'category': 'Human Resources',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This app allow your helpdesk team and helpdesk users to submit expense for reimbursement.""",
    'description':  """

Helpdesk Expense
support ticket expense
support team expense
hr expense
odoo community helpdesk
helpdesk
support ticket
helpdesk app
odoo helpdesk
expense
employee expense
reimbursement
expense reimbursement
hr reimbursement
reimbursement
ticket reimbursement
ticket travel
travel expense            
Travel Request,
Travel Request Confirmation,
Advance Payment Request,
Expenses
employee expense
Expenses Sheet
travel expense
expense advance
advance expense
This module will allow you to manage travel of your employees and expense advance and submit expense claim.
employee travelling
travel expense
travel employee
advance expense
advance salary

expense claim
expense employee
Employee Travel Expense Report
Employee Travel Expense QWEB
Employee Travel Expense PDF
Travel Expense
employee travel
employee travel management
travel app
travel module
employee location
Employee Travel Management
advance expense
expense request
advance request
accounting expense
employee advance expense process
director expense approval
Employee Advance Expense Request 
Employee Advance Expense Request PDF Report
Employee Advance Expense Request QWEB Report
hr employee advance
cash advance
expense advance
advance form
advance request
advance application form
employee advance request
hr_expense
hr_expense_advance
hr_advance
hr expense
hr advance
expense advance form

Employee advance salary
advance salary
salary advance
advance employee
salary advance
employee advance
salary request
advance request
payroll salary
accounting salary
Salary Advances
Salary Advance
Employee Cash Advances
Employee Cash Advance
employee_advance_salary
employee advance salary process
director salary approval
advance request
cash advance
employee cash advance
salary in advance
employee salary
hr payroll
payroll employee
employee hr payroll
payroll


        
                    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    # 'live_test_url': 'https://youtu.be/R3mgJHauq8A',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/helpdesk_expense/252',#'https://youtu.be/3vCS9QC5gFQ',
    'images':   [
                    'static/description/image.png'
                ],
    'depends':  [
                    'hr_expense',
                    'website_helpdesk_support_ticket',
                ],
    'data': [
        'views/hr_expense_view.xml',
        'views/helpdesk_support_view.xml',
            ],
   'installable' : True,
   'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
