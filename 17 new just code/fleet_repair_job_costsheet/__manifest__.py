# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Job Cost Sheet for Fleet Repair Works/Jobs",
    'price': 99.0,
    'currency': 'EUR',
    'version': '8.1.4',
    'category' : 'Human Resources/Fleet',
    'license': 'Other proprietary',
    'summary': """This module allow to create job cost sheet for fleet repair services.""",
    'description': """
Fleet Repair Job Costsheet
This module allow to create job cost sheet for fleet repair services.
Job Cost Sheet for Fleet Repair Works/Jobs
""",
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/image.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/fleet_repair_job_costsheet/738',#'https://youtu.be/1Bofx1tALxI',
    'depends': [
        'fleet_repair_request_management',
        'odoo_job_costing_management',
    ],
    'data':[
        'security/ir.model.access.csv',
        'views/fleet_request_view.xml',
        'views/job_costing_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
