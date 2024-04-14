# Copyright (C) 2019-2021 Artem Shurshilov <shurshilov.a@yandex.ru>
# License OPL-1.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "hr attendance geotracking Android professional policy address mechanism",
    "summary": """
        Module allows you Adnroid app FREE to geotracking your employees
        with GPS coordinates accuracy 1 meter at best, backend part""",
    "author": "EURO ODOO, Shurshilov Artem",
    "maintainer": "EURO ODOO",
    "website": "https://eurodoo.com",
    "live_test_url": "https://eurodoo.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Human Resources",
    "version": "0.0.1",
    "license": "OPL-1",
    "price": 200,
    "currency": "EUR",
    "images": [
        "static/description/preview.jpg",
    ],
    # any module necessary for this one to work correctly
    "depends": ["base", "web", "hr_attendance_base"],
    "external_dependencies": {"python": ["pyproj", "shapely"]},
    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "security/hr_attendance_security.xml",
        "views/views.xml",
        "views/res_config_settings_views.xml",
    ],
    "qweb": [
        "static/src/xml/attendance.xml",
    ],
}
