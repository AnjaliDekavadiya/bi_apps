# Copyright 2019-2024 Artem Shurshilov
# Odoo Proprietary License v1.0

from odoo import http
from odoo.addons.hr_attendance.controllers.main import HrAttendance
from odoo.http import request


class HrAttendanceBase(HrAttendance):
    def get_employee_info_response(self, employee):
        """Общий метод для наследования всех модулей.
        Каждый модуль добавляет свои настройки(параметры)
        которые будут видны на фронтенде

        Arguments:
            employee -- дикт сотрудника, который содержит
        все данные по сотруднику, первое посещение имя ид и прочее
        а также все дополнительные параметры из кастомных модулей
        например настройки распознования или флаг включения/отключения
        конкретного модуля

        Returns:
            employee
        """
        return employee

    # USER AUTH (SYSTRAY)
    # AFTER CHECK IN/OUT
    @http.route("/hr_attendance/systray_check_in_out", type="json", auth="user")
    def systray_attendance(self, latitude=False, longitude=False, context={}):
        # TODO: super inherit
        employee = request.env.user.employee_id
        if context:
            employee = employee.with_context(context)
        geo_ip_response = self._get_geoip_response(
            mode="systray", latitude=latitude, longitude=longitude
        )
        employee._attendance_action_change(geo_ip_response)
        return self._get_employee_info_response(employee)

    # USER AUTH (SYSTRAY)
    # BEFORE CHECK IN/OUT
    @http.route("/hr_attendance/attendance_user_data", type="json", auth="user")
    def user_attendance_data(self):
        res = super().user_attendance_data()

        # добавляем дополнительные параметры,
        # необходимые для работы кастомных модулей
        if res:
            res.update(self.get_employee_info_response(res))
        return res

    # PUBLIC AUTH (KIOSK)
    # AFTER CHECK IN/OUT
    @http.route("/hr_attendance/manual_selection", type="json", auth="public")
    def manual_selection(self, token, employee_id, pin_code, context={}):
        company = self._get_company(token)
        if company:
            employee = request.env["hr.employee"].sudo().browse(employee_id)
            if context:
                employee = employee.with_context(context)
            if employee.company_id == company and (
                (not company.attendance_kiosk_use_pin) or (employee.pin == pin_code)
            ):
                employee.sudo()._attendance_action_change(self._get_geoip_response("kiosk"))
                return self._get_employee_info_response(employee)
        return {}
        # return super().manual_selection(token=token,employee_id=employee_id,pin_code=pin_code)

    # PUBLIC AUTH (KIOSK)
    # BEFORE CHECK IN/OUT
    @http.route("/hr_attendance/attendance_employee_data", type="json", auth="public")
    def employee_attendance_data(self, token, employee_id):
        res = super().employee_attendance_data(token, employee_id)

        # добавляем дополнительные параметры,
        # необходимые для работы кастомных модулей
        company = self._get_company(token)
        if company:
            employee = request.env["hr.employee"].sudo().browse(employee_id)
            if employee.company_id == company:
                res.update(self.get_employee_info_response(res))
        return res
