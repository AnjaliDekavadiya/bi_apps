# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
#See LICENSE file for full copyright and licensing details.

{
    'name': "Project Task from CRM Opportunity/Lead",
    'version': '10.2.25',
    'category': 'Sales/CRM',
    'license': 'Other proprietary',
    'price': 30.0,
    'currency': 'EUR',
    'summary':  """This module allow you to create
                    Task from CRM Opportunity/Lead.""",
    'description': """
Task from CRM Opportunity/Lead
    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/image1.jpg'],
    # 'live_test_url': 'https://youtu.be/TU8krM-KVXY',
    # 'live_test_url': 'https://youtu.be/15knv6qUvE4',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/crm_opportunity_task/260',#'https://youtu.be/U2Aa7TLrDK4',
    'depends': [
                'crm',
                'project',
                ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/crm_lead_task_wizard_view.xml',
        'views/opportunity_task_view.xml',
        'views/project_task_view.xml',
    ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
