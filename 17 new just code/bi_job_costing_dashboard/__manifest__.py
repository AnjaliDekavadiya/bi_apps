# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Project Job Costing Dashboard in Odoo',
    'version': '17.0.0.0',
    'category': 'Project',
    'summary': 'Dashboard for Job Costing Construction Dashboard for project job costing Dashboard for job contracting dashboard Construction Job Costing construction Cost Sheet job contracting system Construction job order Dashboard for Job Order Contractors Dashboard',
    'description': """
        This plugin helps to manage Job Costing Dashboard
		dashboard for project job costing 
		dashboard  for Construction job costing 
		Project Dashboard
		
    """,
    'author': 'BrowseInfo',
    'website' : 'https://www.browseinfo.com',
    'price': 9,
    'currency': 'EUR',
    'depends':    [
        'web','account','sale_management',
        'purchase','stock','hr','project',
        'bi_odoo_job_costing_management',
        'bi_material_purchase_requisitions'],
    'data': [
        'views/labout_material_overhead_line_views.xml',
        'views/dashboard_seach_views.xml',
        'views/bi_odoo_job_costing_management_views.xml',
        'views/job_costing_dashboard_views.xml',
    ],
    'license':'OPL-1',
    'qweb': [
    ],
    'auto_install': False,
    'installable': True,
    'live_test_url' : 'https://youtu.be/T6hwewzCHf0',
    'images':['static/description/Banner.gif'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
