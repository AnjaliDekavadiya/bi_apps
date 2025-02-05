# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "HelpDesk Service Level Agreement (SLA) Analysis",
    'price': 9.0,
    'version': '5.1.5',
    'category': 'Services/Project',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This app provide HelpDesk Service Level Agreement (SLA) with Consumption of estimated hours and delay analysis.""",
    'description':  """
Odoo Helpdesk SLA Delay Analysis
SLA
Service level agreement
SLA Levels
Service Level Agreements
Service Level
SLA Team
Service Level Team
Team SLA
Service Level Contract
Internet Service Provider
SLA Level
Helepdesk SLA level
Helepdesk Service Level Agreements
SLA Level
Service Team
SLA Analysis
Helpdesk SLA Analysis
Help Desk Service Level Agreement (SLA)
SLA
service level agreement
helpdesk sla
sla helpdesk
support sla
sla support
service-level agreement
Service-based SLA

                    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/helpdesk_sla_delay_analysis/485',#'https://youtu.be/8uf_8t4eD1s',
    'images':   [
                    'static/description/image.png'
                ],
    'depends':  [
                    'helpdesk_service_level_agreement',
                ],
    'data': [
                    'views/helpdesk_stage_history_analysis.xml',
                    'views/helpdesk_stage_history_view.xml',
            ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
