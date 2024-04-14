# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. 
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Fleet Repair Integration with Stock Inventory',
    'version': '7.1.7',
    'price': 99.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category' : 'Inventory/Inventory',
    'summary': """Fleet Repair Integration with Stock Inventory""",
    'description': """
Fleet repair
Fleet repair request
Fleet repair management
Fleet Repair Integration Stock Inventory
Fleet repair app
Fleet repair stock inventory
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/image.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/fleet_repair_stock_inventory/734',#'https://youtu.be/D-GGlBe3RYA',
    'depends': [
               'fleet_repair_request_management',
               'stock'
                ],
    'data':[
        'views/stock_move_inherited_view.xml',
        'views/project_task_view_inherit.xml',
        'views/fleet_request_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

