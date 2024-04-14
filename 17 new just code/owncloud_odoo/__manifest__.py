# -*- coding: utf-8 -*-
{
    "name": "ownCloud / Nextcloud Odoo Integration",
    "version": "17.0.1.1.3",
    "category": "Document Management",
    "author": "faOtools",
    "website": "https://faotools.com/apps/17.0/owncloud-nextcloud-odoo-integration-839",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "cloud_base"
    ],
    "data": [
        "data/data.xml",
        "security/ir.model.access.csv",
        "views/clouds_client.xml"
    ],
    "assets": {},
    "demo": [
        
    ],
    "external_dependencies": {
        "python": [
                "pyocclient",
                "six"
        ]
},
    "summary": "The tool to automatically synchronize Odoo attachments with ownCloud/Nextcloud files in both ways. ownCloud synchronization. Nextcloud synchronization. ownCloud connector. Nextcloud connector",
    "description": """For the full details look at static/description/index.html
* Features * 
- How synchronization works
- Internal and public URLs
#odootools_proprietary""",
    "images": [
        "static/description/main.png"
    ],
    "price": "149.0",
    "currency": "EUR",
    "live_test_url": "https://faotools.com/my/tickets/newticket?&url_app_id=46&ticket_version=17.0&url_type_id=3",
}