# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Multiple Branchs/Units Operations by Company',
    'version': '13.5.13',
    'price': 149.0,
    'category' : 'Sales/Sales',
    'license': 'Other proprietary',
    'currency': 'EUR',
    'summary': """This app allow you to manage Odoo operations with Multiple Branches/Units setup.""",
    'description': """
branch
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
Branch on Receipt
Branch on Payment
Branch Wise Accounting Report
probuse

Branch office
organization
branch organization
legal entity
main office
Branching
financial institutions
Branches are a part of the parent organization, which are opened to perform the same business operations as performed by the parent company, to increase their reach.
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
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/odoo_multi_branch/1064',#'https://youtu.be/FeNxy-t9gqE',
    'images': [
               'static/description/image.jpg'
               ],
    'depends': [
        'sale_stock',
        'purchase',
        'calendar',
    ],
    'data':[
        'security/security.xml',
        'security/record_rule.xml',
        'security/ir.model.access.csv',
          #'wizard/account_journal_audit_report_view.xml',
#         'wizard/account_general_ledger_report_view.xml',
#         'wizard/account_financial_report_view.xml',
#         'wizard/account_trial_balance_report_view.xml',
#         'wizard/account_partner_ledger_view.xml',
        'wizard/switch_branch_view.xml',
#         'views/report_financial.xml',
#         'views/report_generalledger.xml',
#         'views/report_trialbalance.xml',
#         'views/report_account_journal.xml',
#         'views/report_partner_ledger_view.xml',
        'report/layout_templates.xml',
        'report/sale_report_view.xml',
        'report/stock_picking_report_view.xml',
        'report/invoice_report_view.xml',
        'report/purchase_order_report_view.xml',
        'report/branch_xpath.xml',
        'views/product_template_view.xml',
        'views/company_branch_view.xml',
#        'views/account_invoice_view.xml', odoo13
        'views/account_move_view.xml',
        'views/analytic_account_view.xml',
        'views/sale_order_view.xml',
        'views/purchase_order_view.xml',
        'views/res_users_view.xml',
        'views/res_partner_view.xml',
        'views/account_bank_statement_view.xml',
        'views/stock_picking_view.xml',
        'views/account_payment_view.xml',
        'views/stock_location_view.xml',
        'views/stock_warehouse_view.xml',
        'views/stock_quant_view.xml',
        'views/procurement_group_view.xml',
        'views/calendar_event_view.xml',
        # 'views/stock_inventory_view.xml', #odoo15
        'views/stock_move_view.xml',
        'views/sales_team_view.xml',
        'views/stock_scrap_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
