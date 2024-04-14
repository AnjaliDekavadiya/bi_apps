# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Courier Management, Courier Request, Courier Shipping Parcel System',
    'version': '1.0',
    'sequence': 1,
    'category': 'Services',
    'description':
        """
 Courier Management Module add below functionality into odoo

        - Courier Management system odoo application adds Courier Management functionality into the odoo. If you are running a courier service then this odoo application will be very useful for you. Create Courier Request for the customer. Add sender and receiver details into the request(name, address, contact etc), add courier details(kilometer, distance charge, additional charge etc)into the request.Add parcel details into the request with quantity, weight, dimension and total charge of the courier will be calculated automatically. Add some parcel images into the request.Take digital signature of sender on the courier request. Define various stages of the request(e.g. collected, dispatched, delivered etc.) Create Customer Invoice for the courier request.Send courier request by email.Various kinds of reports are provided for better understanding 
        Configure Stages for Courier Request

Odoo allows you to set up customized stages for your courier requests. These stages represent the various states or statuses that a courier request can go through, such as "Pending," "In Transit," "Delivered," etc. This feature helps you track the progress of each request easily.
arrow Configure Contacts of courier service, Separate menu for contact is also created

To streamline your courier management, Odoo enables you to maintain a comprehensive list of contacts for your courier service providers. You can create a separate menu for these contacts, making it easy to access their information when needed. This ensures efficient communication with your courier partners
arrow Configure Weight Price Rules

Odoo lets you establish weight-based pricing rules for your courier services. You can define different rates for shipping based on the weight of the packages. This flexibility helps you accurately calculate shipping costs for various items.
arrow Configure Dimension Price Rules

For businesses with shipping needs across different geographic regions, Odoo's distance-based pricing rules come in handy. You can set varying rates depending on the distance packages need to travel, optimizing cost-effectiveness..
arrow Configure Distance Price Rules

Users can create courier requests within Odoo, providing comprehensive details such as sender information, recipient details, package dimensions, weight, shipping stage, and any special instructions. This feature centralizes request creation and management.
arrow Create Courier Request with detailed information of the courier
arrow Create Invoice for the Courier Request

Odoo simplifies the billing process by allowing you to generate invoices directly from courier requests. This integration ensures accurate and timely invoicing, reducing manual work and billing errors.
arrow Send Courier Request by email

With Odoo, you can send courier requests to your service providers via email directly from the system. This feature streamlines communication, making it easy to share courier details and instructions..
arrow Reporting :

    Print Courier Request as PDF Report
    You can generate detailed PDF reports of individual courier requests, containing all relevant information
    Print Courier Request History as PDF Report This report provides a historical overview of courier requests, helping you analyze trends and performance
    View Courier Request Analysis Odoo's analysis tools allow you to gain insights into courier request data, making it easier to optimize your courier management processes. 
        
        Courier Management System
Odoo Shipping Module
Logistics Software
Parcel Tracking
Shipping Management
Package Delivery
Transportation Management
Dispatch Management
Route Optimization
Last-Mile Delivery
E-commerce Shipping
Shipping Integration
Warehouse Management
Express Courier Solutions
Delivery Route Planning
Courier Dispatch Software
Real-time Tracking
Shipping Automation
Odoo Delivery App
Freight Management

Courier Management in odoo,Courier Request,Courier Service, Courier weight and price rules,Courier disctance, Courier Disctacne rules,Courier boy, delivery boy, transport, freight, dispatch courier, courier logistics, courier shipping, courier service tracking, courier invoice bill, courier mails services delivery boy

    """,
    'summary': 'Courier Management in odoo,Courier Request,Courier Service, Courier weight and price rules,Courier disctance, Courier Disctacne rules,Courier boy, delivery boy, transport, freight, dispatch courier, courier logistics, courier shipping, courier service tracking, courier invoice bill, courier mails services delivery boy',
    'depends': ['account'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/stage_data.xml',
        'views/menu_views.xml',
        'views/partner.xml',
        'views/stages_view.xml',
        'views/tags_views.xml',
        'views/category_views.xml',
        'views/type_views.xml',
        'views/priority_views.xml',
        'views/weight_rule_views.xml',
        'views/dimension_price_rule_views.xml',
        'views/distance_price_rule_views.xml',
        'views/courier_request_views.xml',
        'views/res_config_view.xml',
        'views/account_move_views.xml',
        'report/courier_template.xml',
        'report/request_history_template.xml',
        'report/report_menu.xml',
        'data/email_template.xml',
        'report/request_analysis.xml',
        'wizard/request_history.xml',
    ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    # author and support Details =============#
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':49.0,
    'currency':'EUR',
   # 'live_test_url':'https://www.youtube.com/watch?v=935l7f3INE4&list=PLFEwomCwV06U07Zesuj6IVoE1WgsOh5V5',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
