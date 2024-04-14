# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': "Job Costing Contracting and Project Construction Team",
    'version': '17.0.0.0',
    'category': 'Projects',
    'summary': 'Project team for Construction Job Costing construction Team job contracting team Construction job order Material Planning On Job Order Construction Material request purchase Material request Project construction team Labour estimation Construction Budget',
    'description': """The module to manage the team or create a team based on their task or job this module can be helpful for you
	Project Team for  Constrcution and Contracting  Constrcution and Contracting
	Contracting Project Team Constrcution Project Team team project contracting 
	contract for project team project contracting Project Team for Constrcution Project Team Constrcution
	.This module will help to manage team in all industry""",
    'author': "BrowseInfo",
    'website': 'https://www.browseinfo.com',
    "price": 19,
    "currency": 'EUR',
    'depends': ['base', 'bi_material_purchase_requisitions', 'bi_odoo_job_costing_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/project_team_view.xml',
        'views/cost_sheet_tags_view.xml',
        'views/project_view.xml',
        'views/job_orders_view.xml',
        'report/job_cost_sheet_report.xml',
        'report/job_order_report.xml',
    ],
    "auto_install": False,
    "installable": True,
    'license': 'OPL-1',
    "live_test_url": 'https://youtu.be/tkm-c6u2ApE',
    "images": ["static/description/Banner.gif"],

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
