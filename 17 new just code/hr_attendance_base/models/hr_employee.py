# Copyright 2019-2024 Artem Shurshilov
# Odoo Proprietary License v1.0

from odoo import models

ACCESS_ALLOWED = """
        <h5>
            <div>
                <div>
                    <i class="fa fa-check-square-o token-fa-3x" style="color:green"></i>
                </div>
            </div>
        </h5>
"""

ACCESS_ALLOWED_DISABLED = """
        <h5>
            <div>
                <div>
                    <i class="fa fa-check-square-o token-fa-3x" style="color:#ced4da"></i>
                </div>
            </div>
        </h5>
"""


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _parse_additional_vals_from_context(self, mode):
        vals = {}
        if self._context.get("geospatial_id", None):
            vals.update(
                {"geospatial_check_" + mode + "_id": self._context.get("geospatial_id", None)}
            )
            vals.update({"geospatial_access_check_" + mode: ACCESS_ALLOWED})
        elif "geospatial_access_check_" + mode in self:
            vals.update({"geospatial_access_check_" + mode: ACCESS_ALLOWED_DISABLED})
        # if self._context.get("ip_id", None):
        #     vals.update({"ip_check_" + mode + "_id": self._context.get("ip_id", None)})
        # if self._context.get("ip", None):
        #     vals.update({"ip_check_" + mode: self._context.get("ip", None)})
        if self._context.get("geo", None):
            vals.update({mode + "_latitude": self._context.get("geo").get("latitude")})
            vals.update({mode + "_longitude": self._context.get("geo").get("longitude")})
            vals.update({"geo_check_" + mode: self._context.get("geo", None)})
            vals.update({"geo_access_check_" + mode: ACCESS_ALLOWED})
        elif "geo_access_check_" + mode in self:
            vals.update({"geo_access_check_" + mode: ACCESS_ALLOWED_DISABLED})
        # if self._context.get("token", None):
        #     vals.update({"token_check_" + mode + "_id": self._context.get("token", None)})
        # if self._context.get("user_agent_html", None):
        #     vals.update(
        #         {"user_agent_html_check_" + mode: self._context.get("user_agent_html", None)}
        # )
        if self._context.get("face_recognition_image", None):
            vals.update(
                {
                    "face_recognition_image_check_"
                    + mode: self._context.get("face_recognition_image", "").encode()
                }
            )
            vals.update({"face_recognition_access_check_" + mode: ACCESS_ALLOWED})
        elif "face_recognition_access_check_" + mode in self:
            vals.update({"face_recognition_access_check_" + mode: ACCESS_ALLOWED_DISABLED})
        if self._context.get("webcam", None):
            vals.update({"webcam_check_" + mode: self._context.get("webcam", "").encode()})
        # if self._context.get("kiosk_shop_id", None):
        #     vals.update({"kiosk_shop_id_check_" + mode: self._context.get("kiosk_shop_id", None)})

        return vals

    def _attendance_action_change(self, geo_information=None):
        attendance = super()._attendance_action_change(geo_information=geo_information)

        # сохранение полей из контекста, например включили модуль геозон
        # значит в контексте будет находиться геозона пользователя для сохранения
        # или в случае распознования по лицу это может быть фото
        # или в случае геолокации координаты и т.п.
        mode = "out" if self.attendance_state != "checked_in" else "in"
        additional_vals = self._parse_additional_vals_from_context(mode)
        if additional_vals:
            attendance.write(additional_vals)
        return attendance
