# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Job Cost Sheet for Laundry Request",
    'price': 49.0,
    'currency': 'EUR',
    'version': '4.2.2',
    'category' : 'Services/Project',
    'license': 'Other proprietary',
    'summary': """Allow to create job cost sheet for laundry requests.""",
    'description': """
Job Cost Sheet for Laundry Request
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/image.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/laundry_job_cost_sheet/92',#'https://youtu.be/ukqAvhQXhow',
    'depends': [
        'laundry_iron_business',
        'odoo_job_costing_management',
    ],
    'data':[
        'security/ir.model.access.csv',
        'wizard/laundry_request_job_costsheet_view.xml',
        'views/laundry_request_view.xml',
        'views/jobcost_sheet_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
