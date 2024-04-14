from odoo import http
from odoo.http import request
from odoo.tools.translate import _
from datetime import datetime

class FleetAttendanceChecklist(http.Controller):
    
    @http.route('/fleet_attendance_checklist/on_trip_state_changed', type="json", auth='user')           
    def on_trip_state_changed(self, trip_id, trip_state):
        if not trip_id or not trip_state:
            return False
        fleet_attendance = request.env['fleet.attendance'].sudo().browse(int(trip_id))
        if fleet_attendance:
            fleet_attendance.sudo().write({
                'trip_state' : trip_state,
            })

    @http.route('/fleet_attendance_checklist/on_checkin_changed', type="json", auth='user')           
    def on_checkin_changed(self, trip_line_id, checked_in, checked_in_time):
        if not trip_line_id:
            return False
        fleet_attendance_line = request.env['fleet.attendance.line'].sudo().browse(int(trip_line_id))
        if fleet_attendance_line:
            fleet_attendance_line.sudo().write({
                'checked_in' : checked_in,
                'checked_in_time' : checked_in_time,
            })

    @http.route('/fleet_attendance_checklist/on_checkout_changed', type="json", auth='user')           
    def on_checkout_changed(self, trip_line_id, checked_out, checked_out_time):
        if not trip_line_id:
            return False
        fleet_attendance_line = request.env['fleet.attendance.line'].sudo().browse(int(trip_line_id))
        if fleet_attendance_line:
            fleet_attendance_line.sudo().write({
                'checked_out' : checked_out,
                'checked_out_time' : checked_out_time,
            })
    
    @http.route('/fleet_attendance_checklist/on_checkin_alarm', type="json", auth='user')           
    def on_checkin_alarm(self, trip_line_id, type):
        if not trip_line_id or not type:
            return False
        fleet_attendance_line = request.env['fleet.attendance.line'].sudo().browse(int(trip_line_id))
        return fleet_attendance_line.sudo().send_sms(type)

    @http.route('/fleet_attendance_checklist/on_checkout_alarm', type="json", auth='user')           
    def on_checkout_alarm(self, trip_line_id, type):
        if not trip_line_id or not type:
            return False
        fleet_attendance_line = request.env['fleet.attendance.line'].sudo().browse(int(trip_line_id))
        return fleet_attendance_line.sudo().send_sms(type)
    
    @http.route('/fleet_attendance_checklist/on_submit', type="json", auth='user')           
    def on_submit(self, trip_id, state):
        if not trip_id or not state:
            return False
        fleet_attendance = request.env['fleet.attendance'].sudo().browse(int(trip_id))
        state = fleet_attendance.sudo().write({
                'state' : state,
            })
        return state

