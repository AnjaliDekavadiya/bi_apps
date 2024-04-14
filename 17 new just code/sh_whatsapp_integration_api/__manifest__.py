# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "All in one WhatsApp Integration-Sales, Purchase, Account and CRM API | WhatsApp Business | Chat API | Whatsapp Chat API Integration",
    "author": "Softhealer Technologies",
    "website": "http://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Extra Tools",
    "license": "OPL-1",
    "summary": "Whatsapp Odoo Connector,whatsup integration API Chat Invoice To Customer Whatsapp,stock Whatsapp,Sales Whatsapp,Purchase Whatsapp,CRM Whatsapp,Invoice whatsapp,All in one Whatsup Integration,whatsapp integration API,Whatsup Odoo Connector Whatsapp API",
    "description": """Nowadays, There is WhatsApp which is a widely used messenger to communicate with customers and it's faster than compares to emails. But in odoo there is no feature to send an order, documentation to your related customers, vendors, and contacts as well. Our this module will help to send message and orders on WhatsApp it sounds quite familiar, right? so what's new in this app? In this app you no need to go on WhatsApp web page, Just one click to send a message or order to your customer. Just get token and instance from 'Chat Api' and configure that in odoo and go for it.""",
    "version": "0.0.1",
    "depends": ['crm', 'sale_management', 'purchase', 'stock'],
    "application": True,
    "data": [
            "data/sale_order_email_template.xml",
            "data/purchase_order_email_template.xml",
            "data/account_move_email_template.xml",
            "data/account_payment_email_template.xml",
            "data/stock_picking_email_template.xml",

            "security/sh_whatsapp_integration_api_groups.xml",
            "security/sh_whatsapp_integration_api_rules.xml",
            "security/ir.model.access.csv",

            "wizard/sh_send_whatsapp_message_views.xml",
            "views/res_partner_views.xml",
            "wizard/sh_send_whasapp_number_views.xml",

            "views/crm_lead_views.xml",
            "views/sale_order_views.xml",
            "views/purchase_order_views.xml",
            "views/account_move_views.xml",
            "views/stock_picking_views.xml",
            "views/res_config_settings_views.xml",
            "views/res_users_views.xml",
            "views/account_payment_views.xml",
            "views/sh_configuration_manager_views.xml",

            "wizard/sh_qr_code_wizard_views.xml"
    ],
    "images": ["static/description/background.png", ],
    "auto_install": False,
    "installable": True,
    "price": 90,
    "currency": "EUR"
}
