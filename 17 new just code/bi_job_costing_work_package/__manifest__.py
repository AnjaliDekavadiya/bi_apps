# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Job Costing Construction Work Package in Odoo',
    'description': """This app allow you to create and send work package to your customers for your construction and contracting business.
	costing work package 
	job costing work package 
	construction work package 
	costing work package
	
	 For Construction and Contracting please see dependent app to get more details.""",

    'price': 19,
    "currency": 'EUR',
    'summary': 'job costing work package for construction work package for contracting work package job costing contracting work package management costing work package construction job order work package job cost sheet work package Contractor package Labour estimation',
    'category': 'eCommerce',
    'version': '17.0.0.0',
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.com',
    'depends': ['website', 'website_sale', 'stock', 'bi_subtask', 'bi_odoo_job_costing_management',
                'bi_material_purchase_requisitions'],
    'data': [
        'security/ir.model.access.csv',
        'views/work_packages.xml',
        'report/job_work_report.xml',
        'report/job_work_report_view.xml',
        'data/work_mail_template.xml',
    ],
    "auto_install": False,
    'application': True,
    'installable': True,
    "live_test_url": 'https://youtu.be/yMto3FJGNKI',
    "images": ['static/description/Banner.gif'],
    'license': 'OPL-1',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
