# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Agriculture Integration with Job Cost Sheet',
    'price': 49.0,
    'version': '6.1.3',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """Agriculture Integration with Job Cost Sheet.""",
    'description': """
Agriculture Job Cost Sheet
Jobs
Job Types
Agriculture
job cost sheet
job costing
Agriculture job
Agriculture jobs
farm Agriculture
farm job
farm jobs
job contracting
Crop Requests
Crops
Agriculture app
Agriculture Management
Crop Requests
Crops
crop
Agriculture Management Software
Incidents
Dieases Cures
agribusiness
crop yield
agriculture institutes
Farmers
AMS
Farm Locations
farmers
farmer
Agriculture odoo
odoo Agriculture
Agriculture Management System
Animals
print Crop Requests Report
print Crops Report
odoo Agriculture Management Software
Farm Management Software


    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/agriculture_job_cost_sheet/431',#'https://youtu.be/-S4ugmj0oVY',
    'category' : 'Services/Project',
    'depends': [
        'odoo_agriculture',
        'odoo_job_costing_management',
        'odoo_agriculture_website'
    ],
    'data':[
        'views/farmer_cropping_request.xml',
        'views/farmer_location_crops.xml',
        'views/job_costing_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
