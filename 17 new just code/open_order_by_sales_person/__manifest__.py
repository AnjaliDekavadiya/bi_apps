# -*- coding:utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Open Sales Orders by Sales Person(s) Detail',
    'version': '7.1.6',
    'price': 49.0,
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website' : 'www.probuse.com',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category': 'Sales',
    'summary':  """This app allow you to print Open Orders by Sales Person in Excel output.""",
    'description': """
This Module Allow to Export Open Order by Sales Person in Excel.
Open Orders by Item Product
Open Sales Orders by Sales Person
Open Orders by Item
Open Orders by customer
Open Order by customer
Open sale Order by customer
open order
open sale order
open sales
Open sales Order by customer
Open Orders by Product
Open Sales orders by item detail report
Open Items List
open sales order
Sales Open Order Report By Item
sales report
sale order report
order report
sales excel
open orders
open sales order
open sales item
open sales product
sales analysis
sale report
sale order report
stock location
location by product
stock by product
stock by item
inventory by item
inventory by report
stock report
quantity on hand
reserve quantity
sales order open
    """,
    'images': ['static/description/img.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/open_order_by_sales_person/838',#'https://youtu.be/n-INOBde87g',
    'external_dependencies': {'python': ['xlwt']},
    'depends': ['sale_stock','sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/orders_by_sales_person.xml',
        'views/menu.xml',
    ],
    'installable' : True,
    'application' : False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: 

