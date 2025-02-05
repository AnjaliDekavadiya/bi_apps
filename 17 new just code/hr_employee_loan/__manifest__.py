# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Employee Loan Management',
    'version' : '9.6.11',
    'category': 'Human Resources/Employees',
    'depends' : ['account', 'hr', 'hr_contract'
                 # 'hr_payroll'
                ],
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'images': ['static/description/image.jpg'],
    'price': 99.0,
    'currency': 'EUR',
    # 'live_test_url': 'https://www.youtube.com/watch?v=4zYPuB7_XWU&t=9s',
    # 'live_test_url': 'https://youtu.be/FRTcfsawstE',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/hr_employee_loan/423',#'https://youtu.be/VcWdqaYyt5c',
    'license': 'Other proprietary',
    'summary': 'This module allow HR department to manage loan of employees.',
    'website': 'www.probuse.com',
    'support': 'contact@probuse.com',
    'description': ''' 
loan detail report should be verify
This module allow HR department to manage loan of employees
* Loan Request
* Loan Approval
* Loan Disburse
* Loan Repayment
* Loan Policy
* Loan proof
employee loan
loan management
loan
loan request
loan employee
odoo loan
loan for employee
hr loan
human resource loan
loan interest
loan repayment
loan disburse
loan given
loan not from bank
loan from company
company loan to employee
employee loan receive
loan proofs
 ''',
    'demo' : [
            #'views/loan_payroll_demo.xml'
              ],
    'data' : [
        'security/hr_security.xml',
        'security/ir.model.access.csv',
        'views/loan_payroll.xml',
        #'views/prepayment_writeoff_view.xml',
#         'views/loan_payroll_workflow.xml',
        'data/loan_payroll_sequence.xml',
#         'report/loan_payroll_report_view.xml',
#         'wizard/loan_report_wiz_view.xml',
#         'loan_details_report_view.xml',
        'views/payment.xml',#todoprobuse
        'views/loan_proof.xml',
        'report/loan_detail_reg.xml',
        'report/loan_detail_view.xml',
        # 'views/hr_salary_rule_view.xml',
#        comment by probuse 'report/loan_report_view.xml' 
    ],
    'installable': True,
    'application': False,
}
