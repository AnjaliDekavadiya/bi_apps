# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sales Estimate from Machine Repair Request',
    'version': '7.1.5',
    'category' : 'Sales/Sales',
    'depends': [
        'machine_repair_management',
        'odoo_sale_estimates',
    ],
    'price': 59.0,
    'license': 'Other proprietary',
    'currency': 'EUR',
    'summary': """Allow you to create Estimates for Repair Request.""",
    'description': """
Machine Repair Job Estimate.
Allow you to create Sale Estimates for Repair Request.
machine repair
job estimate
sales estimate
estimate
customer estimate
machine repair estimate
    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/machine_repair_job_estimate/467',#'https://youtu.be/w1BSPuUMeqg',
    'data':[
        'security/estimate_security.xml',
        'security/ir.model.access.csv',
        'wizard/machine_job_estimate_wizard_view.xml',
        'views/machine_repair_support_view.xml',
        'views/sale_estimate_view.xml',
        'report/estimate_report_inherit.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
