# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name":"Helpdesk Enterprise",
    "author":"Softhealer Technologies",
    "website":"https://www.softhealer.com",
    "support":"support@softhealer.com",
    "category":"Discuss",
    "license":"OPL-1",
    "summary":"Flexible HelpDesk Customizable Help Desk Service Desk HelpDesk With Stages Help Desk Ticket Management Helpdesk Email Templates Helpdesk Chatter manage customer support ticket system ticket portal support Timesheet Email Alias Email Apps Enterprise Helpdesk Ent Help Desk Enterprise Help Desk Helpdesk Whatsapp Helpdesk Whatsup Helpdesk Odoo",
    "description":"""Are you looking for fully flexible and customisable helpdesk in odoo? Our this apps almost contain everything you need for Service Desk, Technical Support Team, Issue Ticket System which include service request to be managed in Odoo backend. Support ticket will send by email to customer and admin. Customer can view their ticket from the website portal and easily see stage of the reported ticket. This desk is fully customizable clean and flexible. """,
    "version": "0.0.2",
    "depends": ['product','helpdesk_timesheet','project','crm' ,
                'purchase','sale_management'],
    "data": [
        'security/ir.model.access.csv',
        'security/sh_helpdesk_security.xml',
        'data/helpdesk_reminder_cron.xml',
        'data/helpdesk_reminder_mail_template.xml',
        'data/helpdesk_email_data.xml',
        'report/sh_report_helpdesk_enterprise_ticket_template.xml',
        'report/sh_helpdeks_report_portal.xml',
        'report/sh_report_views.xml',
        'wizard/mail_compose_view.xml',
        'views/sh_helpdesk_enterprise_alarm.xml',
        'views/sh_helpdesk_enterprise_category_view.xml',
        'views/sh_helpdesk_enterprise_subcategory_view.xml',
        'views/sh_inherit_helpdesk_team_view.xml',
        'views/sh_inherit_helpdesk_ticket_view.xml',
        'views/sh_helpdesk_enterprise_config_settings_view.xml',
        'views/sh_helpdesk_enterprise_stage.xml',
        'wizard/helpdesk_ticket_update_wizard_view.xml',
        'wizard/helpdesk_ticket_multi_action_view.xml',
        'views/sh_helpdesk_enterprise_ticket_portal_template.xml',
        'views/sh_ticket_feedback_template.xml',
        'views/res_users.xml',
        'views/project_task_views.xml',
        'views/crm_lead_views.xml',
        'views/purchase_order_views.xml',
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'wizard/helpdesk_ticket_megre_wizard_views.xml',
        'views/sh_helpdesk_ticket_stage_info_views.xml',
    ],
     'assets': {
        'web.assets_frontend': [
            'sh_helpdesk_enterprise/static/src/css/feedback.scss',
            'sh_helpdesk_enterprise/static/src/css/bootstrap-multiselect.min.css',
            'sh_helpdesk_enterprise/static/src/js/sh_helpdesk_enterprise_portal.js',
        ],
        'web.assets_backend': [
            'sh_helpdesk_enterprise/static/src/js/bus_notification.js',
            'sh_helpdesk_enterprise/static/src/css/helpdesk_ticket.scss',
        ],
    },
    "application":
    True,
    "auto_install":
    False,
    "installable":
    True,
    "images": [
        'static/description/background.png',
    ],
    "price":
    "200",
    "currency":
    "EUR"
}
