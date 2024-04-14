# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Helpdesk Stage Change History - Enterprise Edition",

    "author": "Softhealer Technologies",

    "website": "https://www.softhealer.com",

    "support": "support@softhealer.com",

    "version": "0.0.1",

    "category": "Discuss",

    "license": "OPL-1",

    "summary": "Helpdesk History Helpdesk State Change History Of Helpdesk Status History Stage Analysis Stage Change Information State Change Information Helpdesk Analysis Odoo",
    "description": """This module helps to display helpdesk stage history. You can find who has moved stage and when. We provide stage change analysis menu where you can see all stages history with details.""",

    'depends': ['helpdesk'],
    'data': [
         "security/ir.model.access.csv",
         "security/sh_helpdesk_state_info_groups.xml",
         "views/helpdesk_ticket_views.xml",
         "views/sh_helpdesk_ticket_info_views.xml",
         "views/sh_helpdesk_ticket_info_menus.xml",

    ],
    'installable': True,
    'auto_install': False,
    'application':True,
    "images": ["static/description/background.png", ],
    "price": "20",
    "currency": "EUR"
}
