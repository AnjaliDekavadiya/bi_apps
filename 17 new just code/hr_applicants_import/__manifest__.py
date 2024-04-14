# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "HR Applications Import from Excel",
    'version': '7.1.14',
    'category': 'Human Resources/Recruitment',
    'summary': 'HR Applications Applicants Import - Import Applications From Excel File',
    'price': 9.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'description':  """
Hr Applications import
recruitment import
hr recruitment import
hr recruitment
hr_recruitment
employee import
Applications import
hr Applications import from excel
applicant import
applicatinos import
               """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/iap.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/hr_applicants_import/490',#'https://youtu.be/V1NozNpJePE',
    'depends': [
            'hr_recruitment'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_applicant_form_view.xml',
        'wizard/hr_applications_import_wizard_view.xml',
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
