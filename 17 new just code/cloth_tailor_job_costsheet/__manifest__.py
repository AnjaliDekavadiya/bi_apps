# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Cloth Tailor with Job Cost Sheet",
    'price': 49.0,
    'currency': 'EUR',
    'version': '5.1.3',
    'category' : 'Project',
    'license': 'Other proprietary',
    'summary': """Create job cost sheet for cloth requests / job costing for tailoring request.""",
    'description': """
Cloth Tailor with Job Cost Sheet
cloth tailor
job cost sheet
cost sheet
job costing
cloth tailoring
tailoring
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/image.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/cloth_tailor_job_costsheet/94',#'https://youtu.be/rL4IMuac3ts',
    'depends': [
        'cloth_tailor_management_odoo',
        'odoo_job_costing_management',
    ],
    'data':[
        'security/ir.model.access.csv',
        'wizard/cloth_request_job_costsheet_view.xml',
        'views/cloth_request_view.xml',
        'views/jobcost_sheet_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
