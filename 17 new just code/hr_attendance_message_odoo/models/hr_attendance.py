import werkzeug.urls

from odoo import fields, models, api


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    check_in_message = fields.Char("Check In Delay Message")
    check_out_message = fields.Char("Check Out Message")
