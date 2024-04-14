# Copyright 2020-2021 Artem Shurshilov
# Odoo Proprietary License v1.0

# This software and associated files (the "Software") may only be used (executed,
# modified, executed after modifications) if you have purchased a valid license
# from the authors, typically via Odoo Apps, or if you have received a written
# agreement from the authors of the Software (see the COPYRIGHT file).

# You may develop Odoo modules that use the Software as a library (typically
# by depending on it, importing it and using its resources), but without copying
# any source code or material from the Software. You may distribute those
# modules under the license of your choice, provided that this license is
# compatible with the terms of the Odoo Proprietary License (For example:
# LGPL, MIT, or proprietary licenses similar to this one).

# It is forbidden to publish, distribute, sublicense, or sell copies of the Software
# or modified copies of the Software.

# The above copyright notice and this permission notice must be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import json

from odoo import http
from odoo.addons.hr_attendance_base.controllers.controllers import (
    HrAttendanceBase,
)
from odoo.http import request


class HrAttendanceGeospatial(HrAttendanceBase):
    @http.route(
        ["/geotracking/enable"],
        type="http",
        auth="public",
        methods=["POST", "GET"],
        csrf=False,
    )
    def geotracking_enable(self):
        return json.dumps({"enable": True})

    @http.route(
        ["/geotracking"],
        type="http",
        auth="public",
        methods=["POST", "GET"],
        csrf=False,
    )
    def geotracking(self, **kw):
        # request.env['hr.attendance'].sudo().search([('employee_id.user_id', '=', request.env.user.id)])
        attendance = (
            request.env["hr.attendance"]
            .sudo()
            .search(
                [("employee_id.user_id", "=", int(kw.get("user_id")))], limit=1
            )
        )
        if not attendance.check_out:
            geo_coords_id = {
                "latitude": kw.get("latitude"),
                "longitude": kw.get("longitude"),
                "hr_attendance_id": int(kw.get("user_id")),
            }
            attendance.geo_coords_ids = [(0, 0, geo_coords_id)]
        geotracking_access_enable = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param(
                str(request.env.user.company_id.id)
                + "hr_attendance_geotracking_access"
            )
        )
        distanse_notify_check_in = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param(
                str(request.env.user.company_id.id)
                + "hr_attendance_distanse_notify_check_in"
            )
        )
        distanse_notify_check_out = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param(
                str(request.env.user.company_id.id)
                + "hr_attendance_distanse_notify_check_out"
            )
        )
        geotracking_batch_mode = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param(
                str(request.env.user.company_id.id)
                + "hr_attendance_geotracking_batch_mode"
            )
        )
        geotracking_period_server_enable = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param(
                str(request.env.user.company_id.id)
                + "hr_attendance_geotracking_period_server_enable"
            )
        )
        geotracking_period_server_qty = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param(
                str(request.env.user.company_id.id)
                + "hr_attendance_geotracking_period_server_qty"
            )
        )
        return json.dumps(
            {
                "geotracking_access_enable": geotracking_access_enable,
                "distanse_notify_check_in": distanse_notify_check_in,
                "distanse_notify_check_out": distanse_notify_check_out,
                "geotracking_batch_mode": geotracking_batch_mode,
                "geotracking_period_server_enable": geotracking_period_server_enable,
                "geotracking_period_server_qty": geotracking_period_server_qty,
            }
        )
