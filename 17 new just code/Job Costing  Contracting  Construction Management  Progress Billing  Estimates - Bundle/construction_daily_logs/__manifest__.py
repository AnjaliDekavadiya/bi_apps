# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. # See LICENSE file for full copyright and licensing details.

{
    'name': 'Construction Daily Logs',
    'version': '6.1.4',
    'license': 'Other proprietary',
    'price': 39.0,
    'category': 'Services/Project',
    'currency': 'EUR',
    'summary': 'Allow user to create Daily logs for construction business.',
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'support': 'contact@probuse.com',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/construction_daily_logs/753',#'https://youtu.be/2NFdKiE4k_o',
    'description': """
daily logs
construction daily logs
Construction Daily Logs
Construction Daily Log
employee daily log
daily log
daily logs
user daily logs
daily log users

 """,
    'depends': ['odoo_job_costing_management'],
    'images': ['static/description/img1.jpg'],
    'data': [
        'views/construction_daily_view.xml',
        'security/ir.model.access.csv',
        'views/construction_daily_report.xml',
        'security/construction_daily_log_security.xml',
        'data/construction_log_templte.xml',
    ],
    'installable': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

