# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Helpdesk Working Hours/Time and Upcoming Holidays",
    'price': 49.0,
    'version': '4.8.1',
    'category': 'Services/Project',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """ Helpdesk Working Hours/Time and Upcoming Holidays  """,
    'description':  """
Odoo Helpdesk Working Hours
working time
helpdesk working time
support working time
public holidays
holidays
support ticket holidays
support ticket
support ticket
odoo community helpdesk
odoo community support ticket
odoo community ticket
support ticket system
odoo helpdesk
public holidays on helpdesk
working schedule for helpdesk
working schedule
team calendar

team working time
team working hours

                    
                    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    # 'live_test_url': 'https://youtu.be/f3oHtfkzZV4',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/helpdesk_working_hours/240',#'https://youtu.be/LdrWONo_WLM',
    'images':   [
                    'static/description/img1.jpg'
                ],
    'depends':  [
                    'website_helpdesk_support_ticket',
                ],
    'data': [
                'views/support_team_view.xml',
                'views/default_working_hours_template_view.xml',
            ],
   'installable' : True,
   'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
