# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Sales Group - Multiple Sales Person on Sales Cycle",
    'price': 49.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """Sales Group - Multiple Sales Person on Sales Cycle""",
    'description': """
    Multiple Sales Person Group
    This module add Sales group on
    Sales Group - Multiple Sales Person on Sales Cycle
    Sales group on customer
    Sales group on crm
    Sales group on quotation
    Sales group on sale order
    Sales group on sale order report
    Sales group on quotation report
    Sales group on sales team
sales people
sales group
sale group
multiple sale person
multiple sales person
multiple sales user
multiple sale user
Sales Group - Multiple Sales Person on Sales Cycle
Sales Group - Multiple Sales Person on Sales Cycle
This module allow you to have multiple sales person / group linked on CRM (Lead and Opportunity), Quotation/Sales Order, Invoice.
Using this module you can configure Sales Group where you are allowed to group multiple sales persons and which will form one group and linked to different documents.
Menu to Configure Sales Group: Sales/Configuration/Sales Groups.
This module allow you to have multiple sales person / group linked on CRM (Lead and Opportunity), Quotation/Sales Order, Invoice.
Using this module you can configure Sales Group where you are allowed to group multiple sales persons and which will form one group and linked to different documents.
Menu to Configure Sales Group: Sales/Configuration/Sales Groups.
sales user
sales cycle multiple person
group of sales person
group sales
sales cycle in group
crm
crm lead
opportunity 
sales activity
sales report
sales person group
sales people group
sales user group
sale person group
sale people group
sale user group
multiple sales man
multiple sales user on sales order
sales order

* INHERIT account.invoice.form (form)
* INHERIT account_user_group_report (qweb)
* INHERIT crm.lead.form (form)
* INHERIT crm.lead.form (form)
* INHERIT crm.team.form (form)
* INHERIT res.partner.form (form)
* INHERIT sale.order.form (form)
* INHERIT sale_user_group_report (qweb)
Sales group form (form)
Sales group tree (tree) 


quotation with multiple sales people
Multiple Sales Person Group

Multiple Sales Person Group.
Multiple Sales Person Group. This module add Sales Groups.
Menus - Sales/Configuration/Sales Groups.

Sales Groups menu on "Sale Configuration".

    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/multiple_sales_person_group/811',#'https://youtu.be/mqkN3asimvA',
    'version': '6.2.1',
    'category' : 'Sales',
    'depends': [
                'sale',
                'crm',
                ],
    'data':[
        'views/sale_user.xml',
        'views/sales_group.xml',
        'views/report_add.xml',
        'security/ir.model.access.csv',
    ],
    'installable' : True,
    'application' : False,
    'auto_install' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
