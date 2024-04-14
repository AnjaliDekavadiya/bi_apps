# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Job Cost Sheet for Car Repair Works/Jobs",
    'price': 69.0,
    'currency': 'EUR',
    'version': '7.2.5',
    'category' : 'Services/Project',
    'license': 'Other proprietary',
    'summary': """This module allow to create job cost sheet for car repair services.""",
    'description': """
Car Repair Request and Management
repair management
Car repair
Car Repair Management Odoo/OpenERP
all type of car repair
car repair website
website car repair request by customer
Car Repair industry
car repair
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
customer car repair
maintenance handling
Car Repair Services
job cost sheet
cost sheet
job costing

    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpeg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/car_repair_job_costsheet/445',#'https://youtu.be/kfJnAaee3Xs',
    'depends': [
        'car_repair_maintenance_service',
        'odoo_job_costing_management',
    ],
    'data':[
        'security/ir.model.access.csv',
        'views/car_repair_support_view.xml',
        'views/jobcost_sheet_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
