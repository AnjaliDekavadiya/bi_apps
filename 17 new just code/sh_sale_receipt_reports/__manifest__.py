# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Sale Order Receipt Report",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "license": "OPL-1",
    "category": "Sales",
    "summary": "Sales Receipt Report SO Receipt Report Sale Orders Receipt Report Sales Report Sale Order Report Quotation Receipt Report Quote Receipt Report Sales Receipt Reports Odoo",
    "description": """This module is useful to print quotation/sale order reports as a receipt. So you can now easily print odoo standard reports in receipt printer. You don't need to switch to another printer.""",
    "version": "0.0.1",
    "depends": [
        "sale_management",
    ],
    "data": [
        "security/sh_sale_receipt_reports_groups.xml",
        "data/sh_sale_receipt_reports.xml",
        "report/external_layout_template.xml",
        "report/sh_sale_receipt_report_templates.xml",
    ],
    "images": ["static/description/background.png", ],
    "auto_install": False,
    "application": True,
    "installable": True,
    "price": 15,
    "currency": "EUR"
}
