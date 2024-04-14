# -*- coding:utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Import POS Orders from Excel',
    'version': '6.5.1',
    'category': 'Sales/Point Of Sale',
    'license': 'Other proprietary',
    'price': 50.0,
    'currency': 'EUR',
    'summary':  """Point of Sales orders from excel file import.""",
    'description': """
Import POS Orders from Excel
import pos
pos order import
pos import
point of sales order import
point of sale order import
import pos order
import pos orders
    """,
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website' : 'www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/ipoe.jpg'],
    #'live_test_url': 'https://youtu.be/22BhDoIEzL4',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/import_pos_orders_excel/805',#'https://youtu.be/GKg3Pe-MKqU',
    'external_dependencies': {'python': ['xlrd']},
    'depends': ['point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/import_pos_orders_excel_view.xml',
        
    ],
    'installable' : True,
    'application' : False,
}
