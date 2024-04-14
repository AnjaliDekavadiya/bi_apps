# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.
{
    'name': "Top Selling Items and Top Customers of Month",
    'price': 19.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """Sales - Top Selling Items and Top Customers of Month""",
    'description': """
    Top Sales by Item Customer
Top Selling Items and Top Customers of Month
probuseTop Selling Items and Top Customers of Month
Top Selling Items and Top Customers of Month
probuse
Top Selling Items and Top Customers of Month


    Top sale by Items Customer
Top Selling Items and Top Customers of Month
probuse
Sales 
Sales  - Top Selling Items and Top Customers of Month
top seller
top customer
top product 
top selling product
top selling items
top sale of month
top selling product of month
month top product
month top items
month top customers
top customer of month
top client

Sales  - Top Selling Items and Top Customers of Month

Created Report Menus:

Top Selling Products
Top Selling Customers
This Module provides feature to print pdf report to show top selling items/products and top selling customers of the month for Sales s. You are allowed to enter on wizard number of product and customer you want to see in top list.
Top Selling Products
sale client
Sales  report
sale report
top sale client
top Sales  customer
top ranking
Sales  data
Sales  report
top seller
top ten
top 10
best customers
best products
best items



""",
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "www.probuse.com",
    'support': 'contact@probuse.com',
    'version': '6.1.4',
    'category' : 'Sales/Sales',
    'images' : ['static/description/image.jpg'],
    'depends': ['sale',
                ],
    # 'live_test_url': 'https://youtu.be/SuB68qSobdM',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/top_sales_by_item_customer/791',#'https://youtu.be/u3CYxvIfs5g',
    'data':[
        'security/ir.model.access.csv',
        'report/top_sale_item_report.xml',
        'report/top_sale_customer_report.xml',
        'wizard/top_sales_items.xml',
        'wizard/top_sale_customers.xml',
        'views/top_sale_report.xml',
        'views/sale_view.xml',
    ],
    'installable' : True,
    'application' : False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
