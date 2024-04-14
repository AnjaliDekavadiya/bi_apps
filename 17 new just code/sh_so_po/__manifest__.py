# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Quick Sale Order To Purchase Order",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Purchases",
    "license": "OPL-1",
    "summary": """Quick Sale Order To Purchase Order So to PO Quotation to Request for quotation Sales to purchase sales order to purchase order quotation to rfq sale to purchase odoo Create Purchase Order From Sale Order Create Purchase Order From Sales Order Purchase Orders From Sale Order RFQ From Quotation Quick Purchase Order Quick RFQ Quick Request For Quotation Purchase From Sales Quick PO Create Sales Order From Purchase Order Quick Purchase Order From Sale Order Quick Purchases Order From Sales Order to Purchase Orders Sale Order to Purchase Orders """,
    "description": """This module is useful to create quickly purchase orders from the sale order. Wasting your important time to make a similar purchase order of your sale order? We will help you to make this procedure quick, just on one click, it will be easy to create a purchase order from quotation or sale order. """,
    "version": "0.0.1",
    "depends": [
        "sale_management",
        "purchase"
    ],
    "application": True,
    "data": [
        "security/ir.model.access.csv",
        "views/sale_views.xml",
        "views/purchase_views.xml",
        "wizard/purchase_order_wizard_views.xml",
    ],
    "images": ["static/description/background.png", ],
    "auto_install": False,
    "installable": True,
    "price": 25,
    "currency": "EUR"
}
