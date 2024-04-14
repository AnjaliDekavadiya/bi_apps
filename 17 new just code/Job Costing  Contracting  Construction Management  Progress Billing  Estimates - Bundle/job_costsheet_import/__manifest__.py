# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Job Cost Sheet Import from Excel",
    'version': '6.1.4',
    'price': 9.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This app will allow you to import Job Cost Sheet from Excel file.""",
    'description': """
job cost sheet
cost sheet
import job cost sheet
job cost sheet import
job costing
job contracting
job costsheet
cost sheet
cost sheet import
import job costing sheet

    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    # 'live_test_url': 'https://youtu.be/Jh2kcAfEM5s',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/job_costsheet_import/230',#'https://youtu.be/YayZcZ0flIM',
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    # 'images': ['static/description/img1.png'],
    'images': ['static/description/image.png'],
    'category' : 'Services/Project',
    'depends': [
                'odoo_job_costing_management',
                ],
    'data':[
            'security/ir.model.access.csv',
            'wizard/import_excel_wizard.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
