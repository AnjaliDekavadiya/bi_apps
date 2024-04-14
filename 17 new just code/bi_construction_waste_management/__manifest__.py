# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Construction Waste management for Job Contracting',
    'description': """This module allow you to manage Construction Waste Materials using scrap and reuse method for your Construction and
	scrap management
	Construction scrap management 
	Recycling Management
	contracting Recycling Management
	contracting waste management
	Constraction scrap management
	Job Contracting business.""",
    'price': 19,
    "currency": 'EUR',
    'summary': 'Waste management for Construction Contracting Waste Materials for Construction Waste Materials for job contracting Scrap Material Waste Materials on Job Order recycle Management for Construction Job Costing Waste Materials construction Scrap Waste Material',
    'category': 'Projects',
    'version': '17.0.0.0',
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.com',
    'depends': ['website', 'website_sale', 'stock', 'bi_subtask', 'bi_odoo_job_costing_management',
                'bi_material_purchase_requisitions'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/inherite_job_order.xml'
    ],
    'license': 'OPL-1',
    'auto_install': False,
    'application': True,
    'installable': True,
    "live_test_url": 'https://youtu.be/kNglDLGJhGU',
    "images": ['static/description/Banner.gif'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
