# Copyright (C) 2019-2024 Artem Shurshilov <shurshilov.a@yandex.ru>
# Odoo Proprietary License v1.0
{
    "name": "hr attendance professional policy technical base",
    "summary": """
        Module provides quick and effective interaction and inheritance
        for all modules dependent on it, forming one eco system""",
    "author": "EURO ODOO, Shurshilov Artem",
    "maintainer": "EURO ODOO",
    "website": "https://eurodoo.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Human Resources",
    "version": "17.0.2.7.1",
    "license": "OPL-1",
    "price": 9,
    "currency": "EUR",
    "images": [
        "static/description/Attendance_base.png",
        "static/description/Attendance_base.png",
        "static/description/Attendance_base.png",
        "static/description/Attendance_base.png",
    ],
    # any module necessary for this one to work correctly
    "depends": ["base", "web", "hr_attendance"],
    # always loaded
    "data": [
        "views/views.xml",
        "security/hr_attendance_security.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "hr_attendance_base/static/src/css/shared.css",
            "hr_attendance_base/static/src/css/sweetalert2.css",
            "hr_attendance_base/static/src/js/lib/sweetalert2.js",
            "hr_attendance_base/static/src/js/shared/shared.js",
            "hr_attendance_base/static/src/js/attendance_menu/attendance_menu.js",
        ],
        "hr_attendance.assets_public_attendance": [
            "/web/static/lib/jquery/jquery.js",
            "hr_attendance_base/static/src/css/kiosk_konfirm.css",
            "hr_attendance_base/static/src/css/shared.css",
            "hr_attendance_base/static/src/js/shared/shared.js",
            "hr_attendance_base/static/src/js/kiosk_confirm/kiosk_confirm.js",
            "hr_attendance_base/static/src/js/kiosk_confirm/kiosk_confirm.xml",
            "hr_attendance_base/static/src/js/public_kiosk/public_kiosk_app.js",
            "hr_attendance_base/static/src/js/public_kiosk/public_kiosk_app.xml",
        ],
    },
}
