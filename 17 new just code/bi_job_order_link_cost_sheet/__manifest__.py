# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Job Cost Sheet Integration with Material Plannings of Costing',
    'version': '17.0.0.0',
    'category': 'Projects',
    'summary': 'Material Planning with Job Cost Sheet creation from job order integration with job costing Material Planning link with job cost sheet job order link with job costing Material Planning integration with job order sheet integration with job order planning',
    'description': """
        Job Order Link Cost Sheet
		Job Cost Sheet from Material Plannings from Job Order
		Cost Sheet from 
		Material Plannings from Job Order
		Job Cost Sheet from Material Plannings from Job Order
		cost sheet link Material Plannings from Job Order
		cost sheet link to job order
		job order cost sheet
		
    """,
    'author': 'BrowseInfo',
    'website' : 'https://www.browseinfo.com',
    'price': 39,
    'currency': 'EUR',
    'depends': ['web','sale_management','purchase','stock','hr','project','bi_odoo_job_costing_management','bi_material_purchase_requisitions'],
    'data': [
        'security/ir.model.access.csv',
        'views/job_order_link_cost_sheet_views.xml',
    ],
    'qweb': [
    ],
    'auto_install': False,
    'license': 'OPL-1',
    'installable': True,
    'live_test_url' : 'https://youtu.be/QEIioYOqT2Q',
    'images':['static/description/Banner.gif'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
