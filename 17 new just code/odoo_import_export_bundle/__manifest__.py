# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.
{
    'name': "Import Export Bundle Apps",
    'price': 1.0,
    'version': '5.1.6',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """Import Export Bundle Apps.""",
    'description': """
import product
product import excel
import product image
product image import excel
import customer
user import
customer import excel
import supplier
import customer supplier
product import
Import Bill of Material
Import Customer/Supplier Invoice
Import Order
supplier import
partner import
import partner
user import
employee import
employee image import
lead import
import lead excel
sale order import
import sale order
import crm lead
import employee image excel
import invoice
invoice import excel
import taxes
import bank statement line
import payments
import account budget
import bom
export bom
odoo import
Import purchase order
Import purchases
Import purchase
purchase order import
import purchase
import purchase order odoo
import purchase order
purchase order import
purchase import
purchase entries import
import purchase entries
import expense
import expense line
import expenses
import expense lines
import expense sheet
import expense sheets
excel expense import
import execl import
csv expense
expense sheet import
expense import
expense line import
expenses import
opening entry import
opening balance import
partner balance import
purchase order excel import
purchase order excel import
import
bom import
project import
task import
tasks import
import pricelist
pricelist import
pricelist item
price list import
import price list
import pricelist items
pricelist excel
excel pricelist
pricelist csv
csv pricelist
import project
import task
import tasks
project task import
import project task
import bom
bill of material import

    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    'category' : 'Sales/Sales',
    'depends': [
                'odoo_import_product_image',
                'odoo_product_import_excel',
                'odoo_customer_supplier_import_csv',
                'odoo_journal_entry_import',
                'user_import_excel_odoo',
                'odoo_import_employee_image',
                'odoo_import_employee_excel',
                'crm_lead_import_excel',
                'sale_order_import_excel',
                'purchase_order_import_excel',
                'invoice_import_excel',
                'odoo_chart_account_import',
                #'import_taxes_excel',
                # 'odoo_import_bank_statement_line',
                'import_payment',
                #'odoo_account_budget_excel',
                'odoo_import_export_bom',
                'odoo_invoice_import',
                'multiple_journal_entry_import',
                'odoo_purchase_order_import',
                'multiple_bom_import',
                'odoo_expense_import_excel',
                'odoo_project_task_import',
                'import_analytic_account',
                'odoo_import_pricelist',
                'import_picking_incoming_outgoing',
                'hr_applicants_import',
                'import_daily_currency_rates',
                'product_lot_serial_import',
                'odoo_fleet_vehicle_import',
                ],
    'data':[
    ],
    'installable' : True,
    'application' : False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
