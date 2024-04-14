# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Machine Reapir Inspection Portal for Customer",
    'version': '5.2.3',
    'license': 'Other proprietary',
    'category': 'Services/Project',
    'price': 39.0,
    'currency': 'EUR',
    'summary':  """Customers to view machine job inspection on my account portal""",
    'description': """

       This app allows your customers to view machine repair inspection on my account portal of your website.
Machine Repair Inspection Portal
Customer / Portal Machine Repair Inspection

    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/mjri.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/machine_repair_job_inspection_portal/465',#'https://youtu.be/TBcjHXKkN9Q',
    'depends': ['machine_repair_job_inspection','portal'],
    'data': [
            'security/inspection_security.xml',
            'security/ir.model.access.csv',
            'views/repair_order_inspection_view.xml',
            'views/repiar_order_portal_templates.xml',
            ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
