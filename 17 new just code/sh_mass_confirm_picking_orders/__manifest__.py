# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Mass Confirm Picking Order From Inventory",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "license": "OPL-1",
    "category": "Warehouse",
    "summary": "Validate Multiple Picking, Mass Conform Delivery Order, Mass Validate Delivery Order,  Mass Validate Picking Order, Bunch Validate Picking, Incoming Order Pack Validate, Mass Confirm Pickings Odoo",
    "description": """When you have bulk pickings then it's very difficult to validate every picking one by one. This module provides functionality to validate all pickings from the inventory. The user has to select the pickings from the list view and then validate all pickings. It shows notification in success.""",
    "version": "0.0.1",
    "depends": ["stock"],
    "data": [
            "security/ir.model.access.csv",
            "wizard/sh_mass_confirm_picking_views.xml",
            "wizard/sh_picking_warning_message_views.xml",
            ],
    "images": ["static/description/background.png", ],
    "application":True,
    "auto_install": False,
    "installable": True,
    "price": "30",
    "currency": "EUR"
}
