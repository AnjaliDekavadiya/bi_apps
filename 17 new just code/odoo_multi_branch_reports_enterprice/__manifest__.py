# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Multi Branch Enterprise Accounting Reporting',
    'price': 199.0,
    'category' : 'Accounting',
    'version': '5.1.1',
    'license': 'Other proprietary',
    'currency': 'EUR',
    'summary': """This app allow you to filter listed enterprise accounting reports by branches.""",
    'description': """
enterprise report
enterprise reporting
account reports
accounting report
Reporting
Profit and Loss
Balance Sheet
Cash Flow Statement
Executive Summary
Check Register
Partner Ledger
General Ledger
Aged Receivable
Aged Payable
Trail Balance
Tax Report
multi branch
multi unit
branch operation
Unit operation
Multiple Branch  Management Module for single company
Multiple  Unit  Management Module for single company
branches
odoo branch
branch concept
multi branch odoo
odoo multi branch
multi companies
multi company
odoo multi branches
different branch
Add multiple unit
Add multiple branch
branch manager
Branch wise Financial Statement
unit wise Financial Statement
odoo branch
odoo unit
odoo branch operation
res.branch
branch odoo
unit odoo
cost center odoo
Branch On Sales
Branch on Picking 
Branch on Delivery Order
Branch On Invoices
Branch On Purchase
Branch On Warehouse
Branch on Session
Branch on pos
pos branch
pos multi branch
point of sale multi branch
Branch on POS order
Branch on pos Receipt
Branch on Receipt
Branch on Payment
Branch Wise Accounting Report
Trial Balance Report
Partner Ledger Report
Branch office
outlet of a company
company outlet
organization
branch organization
subsidiary 
company subsidiary 
branch subsidiary 
legal entity
main office
Branching
financial institutions
Head office
parent company
branch location
store location
branch setup
branch configuration
branch configure
odoo multi branch
company branch
branch company
odoo by branch
sale branch
sales branch
odoo branches
branches
sale branch detail
branch odoo
multi company branch
branch multi
multi branch
company branch
company unit
unit company
    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'images': [
               'static/description/img.jpg'
               ],
    'depends': [
        'odoo_multi_branch',
        'account_reports',
    ],
    'data':[
        'security/security.xml',
        'views/account_report_view.xml',
        # 'views/search_template_view.xml',
    ],
    'installable' : True,
    'application' : False,
    'assets': {
        'web.assets_backend': [
            'odoo_multi_branch_reports_enterprice/static/src/components/**/*',
        ],
    }
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
