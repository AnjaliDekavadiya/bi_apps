# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Job Cost Sheet for Machine Repair Works/Jobs",
    'price': 9.0,
    'currency': 'EUR',
    'version': '7.1.4',
    'category' : 'Services/Project',
    'license': 'Other proprietary',
    'summary': """This module allow to create job cost sheet for machine repair services.""",
    'description': """
Machine Repair Request and Management
This module develop to full fill requirements of Machine Repair Services Provider or Industry.
repair management
Machine repair
Machine Repair Management Odoo/OpenERP
all type of machine repair
machine repair website
website machine repair request by customer
Machine Repair industry
machine repair
fleet repair
car repair
bike repair
fleet management
odoo repair
repair odoo
machine maintenance
maintenance odoo
repair maintenance
maintenance management
fleet maintenance
odoo maintenance
maintenance request
repair request
repair online
repair customer machine
customer machine repair
maintenance handling
Machine Repair Services
job cost sheet
cost sheet
job costing

    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/machine_repair_job_costsheet/457',#'https://youtu.be/2ET_QG90dRg',
    'depends': [
        'machine_repair_management',
        'odoo_job_costing_management',
    ],
    'data':[
        'security/ir.model.access.csv',
        'views/machine_repair_support_view.xml',
        'views/jobcost_sheet_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
