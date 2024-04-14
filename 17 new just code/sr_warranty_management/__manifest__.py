# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

{
    "name": "Product Warranty & Claim Management",
    "version": "1.0",
    "category": "Sales/Sales",
    "summary": "Product Warranty Management product warranty claim management tracking warranty periods processing warranty claims Odoo warranty and claim management manage the warranty process",
    "description": """
        Product Warranty Management
        Product Warranty Claim Management
        Tracking warranty periods
        processing warranty claims
        odoo warranty and claim management
        manage the warranty process
        Streamline Your Warranty and Claim Management with Odoo
        Simplify Your Product Warranty Management with Odoo
        Take Control of Your Warranty and Claims Process with Odoo
        Manage Your Product Warranties Like a Pro with Odoo
        Boost Customer Satisfaction with Odoo's Warranty and Claim Management Application
        Odoo's Warranty and Claim Management: The Solution to Your Warranty Management Challenges
        Reduce Costs and Improve Efficiency with Odoo's Warranty and Claim Management
        Odoo's Warranty and Claim Management: The Key to Successful Product Support
        Efficiently Manage Your Warranty Claims with Odoo's User-Friendly Application
        Odoo's Warranty and Claim Management: The Tool to Deliver Excellent Customer Service.
        Sitaram Solutions developed odoo application named Product Warranty and Claim management
        Streamline Your Warranty and Claim Management Process with Odoo
        Efficiently Manage Product Warranties with Odoo's Warranty and Claim Management Module
        Simplify Your Customer Support with Odoo's Warranty and Claim Management Application
        Maximize Your Warranty Claim Management Efficiency with Odoo
        Empower Your Business with Odoo's Warranty and Claim Management System
        Enhance Customer Satisfaction with Odoo's Warranty and Claim Management Solution
        Efficient Product Warranty Management with Odoo
        Streamline Your Business with Odoo's Warranty & Claim Management Module
        Maximizing Customer Satisfaction with Odoo's Warranty Management Application
        Simplify Your Warranty Management Process with Odoo
        Track and Analyze Your Product Warranties with Odoo
        Optimizing Claim Management with Odoo's Warranty Module
        Improve Your Business Operations with Odoo's Warranty and Claim Management Solution
        Effective Warranty and Claim Management with Odoo's Application
        Odoo's Warranty Module: The Key to Efficient Claim Management
        Stay Ahead of Your Warranty and Claim Management Game with Odoo
        inherit sales order
        inherit product template
        inherit product variant
        inherit account move
        inherit customer invoice
        
    """,
    "price": 25,
    "currency": 'EUR',
    "author": "Sitaram",
    "depends": ["base", "stock", "sale_management", "account"],
    "data": [
        "security/ir.model.access.csv",
        "security/sr_warranty_config_group.xml",
        "data/ir_sequence_data.xml",
        "data/ir_cron_warranty_expired.xml",
        "data/ir_cron_warranty_expire_notification.xml",
        "views/sr_product_warranty_view.xml",
        "views/inherited_product_template.xml",
        "views/inherited_sale_order_view.xml",
        "views/sr_warranty_configuration_view.xml",
        "views/sr_claim_warranty_view.xml",
        "views/sr_warranty_report.xml",
        "views/sr_claim_report.xml",
        "views/inherited_product_view.xml",
        "views/inherited_account_move_view.xml",
        "wizard/sr_renew_warranty_view.xml",
        "wizard/sr_claim_warranty_wizard_view.xml",
        "wizard/sr_claim_refuse_reason_view.xml",
        "wizard/sr_warranty_report_wizard_view.xml",
        "wizard/sr_claim_report_wizard_view.xml",
        "views/sr_reporting_menu_view.xml",
        "report/sr_warranty_report_template.xml",
        "report/sr_report_warranty_templates.xml",
        "report/sr_warranty_report_action.xml",
        "report/sr_claim_report_template.xml",
        "report/sr_report_claim_templates.xml",
        "report/sr_claim_report_action.xml",
    ],
    "website": "https://sitaramsolutions.in",
    "application": True,
    "installable": True,
    "auto_install": False,
    "live_test_url": "https://youtu.be/7H-6z1Q3VWM",
    "images": ['static/description/banner.png'],
    "license": "OPL-1",
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
