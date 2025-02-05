# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.
{
    'name': "Sales Team Member(s) Limited Customers",
    'version': '9.1.2',
    'price': 42.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """Limited Customers / Contacts for Sales Team Members""",
    'description': """
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
many sales person
SalesPerson can view only customers where he/she set as Sales person
Allow you to set multiple sales person on customer form.
SalesPerson on Quote/Sales order can view his own customers only.
SalesPerson on Invoice/Bill can view his own customers only.
Own customers on sales order and invoice forms for sales person login.
Allow your Salesperson can see Own Customer.
Allow your Salesperson can see Own Customer into sale order.
Allow your Salesperson can see Own Customer into Invoices.
Manager can assign multiple sales person to one customer
For Sales Person you can add many sales person for single customer
Add Multipe or one salesperson into salesperson field on customer form.
Salesperson can access own customer only in menus.
For more details please see below screenshot and video.
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
    'website': "www.probuse.com",
    'support': 'contact@probuse.com',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/sales_team_customer_access/118',#'https://youtu.be/cSpchOaGXUs',
    'images': ['static/description/image.png'],
    'category' : 'Sales',
    'depends': ['sales_person_customer_access'],
    'data':[
        'views/res_partner_view.xml',
        'security/record_rule.xml',
    ],
    'installable' : True,
    'application' : True,
    'auto_install' : False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
