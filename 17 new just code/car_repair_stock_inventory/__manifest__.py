# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. 
# See LICENSE file for full copyright and licensing details.

{
    'name': 'CAR Repair Integration with Stock Inventory',
    'version': '7.1.4',
    'price': 49.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category' : 'Inventory/Inventory',
    'summary': """CAR Repair Integration with Stock Inventory""",
    'description': """
CAR repair
CAR repair request
CAR repair management
CAR Repair Integration Stock Inventory
CAR repair app
car repair stock inventory

    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/image.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/car_repair_stock_inventory/448',#'https://youtu.be/pwrl9byXVnw',
    'depends': [
               'car_repair_maintenance_service',
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

