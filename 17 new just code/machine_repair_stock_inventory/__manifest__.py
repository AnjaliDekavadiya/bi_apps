# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. 
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Machine Repair Integration Stock Inventory',
    'version': '7.1.5',
    'price': 49.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category' : 'Inventory/Inventory',
    'summary': """Machine Repair Integration with Stock Inventory""",
    'description': """
machine repair
machine repair request
machine repair management  
Machine Repair Integration Stock Inventory
machine repair app

    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    #'live_test_url': 'https://youtu.be/3Ki0ldwgXrw',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/machine_repair_stock_inventory/3',#'https://youtu.be/FTqIRITFGVw',
    'depends': [
               'machine_repair_management',
               'stock'
                ],
    'data':[
        'views/stock_move_inherited_view.xml',
        'views/project_task_view_inherit.xml',
        'views/machine_repair_view_inherit.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

