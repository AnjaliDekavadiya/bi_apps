# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Sales Team Members Access to Sales Order of Team",
    'price': 80.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This module allow team members in same team to have read/modify access to quote/sales order.""",
    'description': """
        Sale Team management
This module allow team members in same team to have read/modify access to quote/sales order.
 allow sales team member to see sales order
    team access
    sale order access to sales team
    sales order team access

Sales Person Customer Access
Allow Partner Access
Salesperson can access own customer in sale order
Salesperson can access own customer in quotation
Allow customer Access
allow vendor access
Salesperson Own Customer & Sale Orders
Salesperson Own Customer
Sale Orders
invoice
Allow Salesperson can see Own Customer
Allow Salesperson can see Own Customer into sale order 
sales person
salesperson
partner access
customer access
vendor access
sales person access
Salesperson access
Salesperson rights
Salesperson rules
Salesperson record rules
Salesperson idea
Salesperson restriction
Salesperson limit
Salesperson limitation
Salesperson data
Salesperson work
access customer
access partner
access vendor
multi Salesperson
multi Sales person
sales team
team sales
multiple Salesperson
multiple Sales person
team Salesperson
Salesperson team
Salesperson selection
sale order access to sales team
sales order team access
sales order team access
invoice access
team access
sales access
invoice access
sales order team access 
Salesperson invoice access
Salesperson sales Salesperson
sales order access
purchase order access
multi user
multi Salesperson
multi team
Salesperson Own Customer
Salesperson Own Customers
own customers
my customer
Salesperson customer
Salesperson customers
restricted customers
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/sale_team_order_access/769',#'https://youtu.be/tIIm5ayrEMA',
    'version': '6.4.1',
    'category' : 'Sales',
    'depends': ['sale','sales_team'],
    'data':[
        'security/security_order.xml',
    ],
    'installable' : True,
    'application' : False,
    'auto_install' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
