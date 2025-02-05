# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Waste Management for Construction and Contracting',
    'version': '7.4.1',
    'category' : 'Projects/Projects',
    'license': 'Other proprietary',
    'depends': [
               'odoo_job_costing_management',
                ],
    'price': 20.0,
    'currency': 'EUR',
    'summary': """Waste Management for Construction and Job Contracting Industry.""",
    'description': """
waste Management
construction waste
construction waste Management
scrap
product scrap
Discarded material
construction waste
Demolition and deconstruction
deconstruction
Demolition
demolition waste
recycled
landfill
Special waste
Reuse materials
construction
job contracting
job construction
job cost sheet
cost sheet
material planning
material plan
waste material
composted
Construction and demolition waste
waste management plan
reuse material

    
""",
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    # 'images': ['static/description/img.jpg'],
    'images': ['static/description/img.png'],
    #'live_test_url': 'https://youtu.be/RsNdH9RTs-U',
    # 'live_test_url': 'https://youtu.be/1VPRiY26Y9E',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/construction_waste_management/263',#'https://youtu.be/n6RDuZVVYVU',
    'data':[
        'security/ir.model.access.csv',
        'security/waste_materials_security.xml',
        'data/waste_sequence.xml',
        'views/construction_management_view.xml',
        'views/project_view.xml',
        'views/stock_picking_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
