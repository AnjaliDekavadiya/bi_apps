# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "CRM Stage Change History | Pipeline Stage Change History",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "version": "0.0.1",
    "category": "Sales",
    "license": "OPL-1",
    "summary": "CRM Order History In Product Pipeline Order History In Product Opportunity Order History In Product Lead History CRM History Pipeline History Opportunity History Change Stage History Stage Analysis Odoo",
    "description": """This module helps to display CRM(opportunity/pipeline) stage history. You can find who has moved stage and when. We provide stage change analysis menu where you can see all stages history with details.""",
    'depends': ['crm'],
    'data': [
         "security/ir.model.access.csv",
         "security/security_groups.xml",
         "views/crm_lead_task_info.xml"

    ],
    'installable': True,
    'auto_install': False,
    'application':True,
    "images": ["static/description/background.png", ],
    "price": "20",
    "currency": "EUR"
}
