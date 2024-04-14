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
    "name": "Fleet Attendance Checklist | Fleet Vehicle Attendance Sheet",
    "summary": """
        This module allows the odoo portal users to mark partner attendance on fleet attendances.  the user may mark either a return journey 
        or an onward trip for check-in and check-out. they can print the attendance report as well.
    """,
    "version": "17.1",
    "description": """
        This module allows the odoo portal users to mark partner attendance on fleet attendances.  the user may mark either a return journey 
        or an onward trip for check-in and check-out. they can print the attendance report as well.
        Fleet Attendance Checklist,
        Fleet Vehicle Attendance Sheet,
        Fleet Attendance,
    """,    
    "author": "CFIS",
    "maintainer": "CFIS",
    "license" :  "Other proprietary",
    "website": "https://www.cfis.store",
    "images": ["images/fleet_attendance_checklist.png"],
    "category": "Extra Tools",
    "depends": [
        "base",
        "fleet",
        "portal",
        "sms",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "report/reports.xml",
        "report/report_template.xml",
        "views/fleet_passengers_views.xml",
        "views/fleet_vehicle_views.xml",
        "views/fleet_attendance_views.xml",
        "views/fleet_attendance_templates.xml",
        "views/res_partner_views.xml",
    ],
    "assets": {   
        "web.assets_frontend": [
            "/fleet_attendance_checklist/static/src/css/*.css",
            "/fleet_attendance_checklist/static/src/js/*.js",
        ],
    },     
    "installable": True,
    "application": True,
    "price"                 :  210.00,
    "currency"              :  "EUR",
}
