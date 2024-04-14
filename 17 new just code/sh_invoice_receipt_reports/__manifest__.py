# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Invoice Receipt Report",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "license": "OPL-1",
    "category": "Accounting",
    "summary": "Invoice Report, Account Report, Bill Receipt Report, Payment Receipt Report, Invoices Receipt Report, Account Receipt Report, Invoices Report, Accounting Receipt Report Odoo",
    "description": """This module is useful to print the invoice, bill, payment & receipt reports as a receipt. So you can now easily print odoo standard reports in receipt printer. You don't need to switch to another printer.""",
    "version": "0.0.1",
    "depends": [
        "account",
    ],
    "application": True,
    "data": [
        "security/sh_invoice_receipt_reports_groups.xml",
        "data/sh_invoice_receipts_reports.xml",
        "report/external_layout_template.xml",
        "report/invoice_payment_template.xml",
        "report/invoice_receipt_template.xml",

    ],
    "images": ["static/description/background.png", ],
    "auto_install": False,
    "installable": True,
    "price": 15,
    "currency": "EUR"
}
