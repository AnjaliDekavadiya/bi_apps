# -*- coding: utf-8 -*-
#################################################################################
# Author      : CFIS (<https://www.cfis.store/>)
# Copyright(c): 2017-Present CFIS.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://www.cfis.store/>
#################################################################################

{
    "name": "Lunch Kiosk Mode | Lunch Authentication | Lunch Kiosk Face Recognition | Lunch Kiosk Facerecognition",
    "summary": """
        This module gives the lunch module a new kiosk feature that allows customers to order lunch with their PIN and Face recognition features.
    """,
    "version": "17.1",
    "description": """
        This module gives the lunch module a new kiosk feature that allows customers to order lunch with their PIN and Face recognition features.
        Lunch Kiosk Mode
        Lunch Authentication
        Face recognition.
    """,    
    "author": "CFIS",
    "maintainer": "CFIS",
    "license" :  "Other proprietary",
    "website": "https://www.cfis-apps.com",
    "images": ["images/lunch_kiosk_mode_adv.png"],
    "category": "Sales",
    "depends": [
        "base",
        "lunch",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/lunch_kiosk_views.xml",
        "views/lunch_product_views.xml",
        "views/res_users_views.xml",
        "views/res_config_settings.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/lunch_kiosk_mode_adv/static/src/lib/source/*.js",
            "/lunch_kiosk_mode_adv/static/src/js/*.*",
        ],
    },   
    "installable": True,
    "application": True,
    "price"                 :  500.00,
    "currency"              :  "EUR",
    "pre_init_hook"         :  "pre_init_check",
}
