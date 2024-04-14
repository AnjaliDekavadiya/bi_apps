# -*- coding: utf-8 -*-
{
    "name": "Reminder Designer and Periodic Reporting",
    "version": "17.0.1.3.3",
    "category": "Extra Tools",
    "author": "faOtools",
    "website": "https://faotools.com/apps/17.0/reminder-designer-and-periodic-reporting-816",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "mail"
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/total_notify.xml",
        "views/res_partner.xml",
        "data/mail_template.xml",
        "data/data.xml",
        "reports/notify_report.xml",
        "reports/notify_report_template.xml",
        "data/cron.xml"
    ],
    "assets": {
        "web.assets_backend": [
                "total_notify/static/src/views/fields/*.js",
                "total_notify/static/src/views/fields/*.xml"
        ]
},
    "demo": [
        
    ],
    "external_dependencies": {
        "python": [
                "xlsxwriter"
        ]
},
    "summary": "The tool to design, generate, and periodically send reports and reminders. Report designer. List generator. Auto reminders. Data export. Recurrent report. Regular statistics. List reminder. Periodic reporting. Table reminder. Excel format. Excel template. Dynamic report. Custom report. Dynamic excel report. Odoo data. Professional report. Excel report designer. Template report. Scheduled notifications. XLSX report. PDF report. Sales reminder. CRM reminder. Activity reminder. Overdue Activities. Events reminder. Meetings reminder. Recurring activities. Recurrent notifications. Report editor. Recurrent reminder. Daily reminder. Daily agenda. To-do list.",
    "description": """For the full details look at static/description/index.html
* Features * 
- Topical and up-to-date reports
- Configurable report appearance
- Flexible periodicity of reports
- List reminders for any business purpose
#odootools_proprietary""",
    "images": [
        "static/description/main.png"
    ],
    "price": "198.0",
    "currency": "EUR",
    "live_test_url": "https://faotools.com/my/tickets/newticket?&url_app_id=6&ticket_version=17.0&url_type_id=3",
}