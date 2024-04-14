# -*- coding: utf-8 -*-
{
    "name": "Smart Alerts",
    "version": "17.0.1.0.9",
    "category": "Productivity",
    "author": "faOtools",
    "website": "https://faotools.com/apps/17.0/smart-alerts-851",
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
        "views/smart_warning.xml",
        "data/data.xml"
    ],
    "assets": {
        "web.assets_backend": [
                "smart_warnings/static/src/views/form/*.js",
                "smart_warnings/static/src/views/form/*.scss"
        ]
},
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "The tool draws users' attention to essential document details and warnings. Raise warnings. Invoice alerts. Sale alerts. Lead alerts. Contact alerts. Dynamic warnings. Alert messages. Auto reminder. Form notifications. Configurable warnings. User alerts. Dynamic alerts.",
    "description": """For the full details look at static/description/index.html
* Features * 
- Typical use cases
#odootools_proprietary""",
    "images": [
        "static/description/main.png"
    ],
    "price": "48.0",
    "currency": "EUR",
    "live_test_url": "https://faotools.com/my/tickets/newticket?&url_app_id=91&ticket_version=17.0&url_type_id=3",
}