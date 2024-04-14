# Copyright 2019-2021 Artem Shurshilov
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

from odoo import api, fields, models


class ResConfigSettingsGeotracking(models.TransientModel):
    _inherit = "res.config.settings"

    geotracking_access = fields.Boolean(
        string="Enable geotracking access",
        help="When users check in store geo coords periodically",
    )
    distanse_notify_check_in = fields.Integer(
        string="Distance push notification check in",
        help="Distance metr, for send pish notification when user should check in",
        default=0,
    )
    distanse_notify_check_out = fields.Integer(
        string="Distance push notification check out",
        help="Distance metr, for send pish notification when user should check out",
        default=0,
    )
    geotracking_batch_mode = fields.Integer(
        string="Quantity in batch (use for reduce server load)",
        help="How many geolocation requests to send to the server, 0 - send every time",
        default=0,
    )
    geotracking_period_server_enable = fields.Boolean(
        string="Manage geotracking period",
        help="Manage the geotracking period from the server,if falsely the client can set the period himself",
        default=False,
    )
    geotracking_period_server_qty = fields.Integer(
        string="Geotracking period milliseconds 1000 = 1 second ",
        help="Manage the geotracking period from the server, geotracking period qty",
        default=1000 * 60 * 30,
    )
    # notify_left_users = fields.Integer(string='Geotracking period milliseconds 1000 = 1 second ',
    #                                         help="Manage the geotracking period from the server, geotracking period qty",
    #                                         default=1000 * 60 * 30)

    def set_values(self):
        res = super().set_values()
        config_parameters = self.env["ir.config_parameter"]
        config_parameters.set_param(
            str(self.env.user.company_id.id)
            + "hr_attendance_geotracking_access",
            self.geotracking_access,
        )
        config_parameters.set_param(
            str(self.env.user.company_id.id)
            + "hr_attendance_distanse_notify_check_in",
            self.distanse_notify_check_in,
        )
        config_parameters.set_param(
            str(self.env.user.company_id.id)
            + "hr_attendance_distanse_notify_check_out",
            self.distanse_notify_check_out,
        )
        config_parameters.set_param(
            str(self.env.user.company_id.id)
            + "hr_attendance_geotracking_batch_mode",
            self.geotracking_batch_mode,
        )
        config_parameters.set_param(
            str(self.env.user.company_id.id)
            + "hr_attendance_geotracking_period_server_enable",
            self.geotracking_period_server_enable,
        )
        config_parameters.set_param(
            str(self.env.user.company_id.id)
            + "hr_attendance_geotracking_period_server_qty",
            self.geotracking_period_server_qty,
        )
        return res

    @api.model
    def get_values(self):
        res = super().get_values()
        res.update(
            geotracking_access=self.env["ir.config_parameter"].get_param(
                str(self.env.user.company_id.id)
                + "hr_attendance_geotracking_access"
            )
        )
        res.update(
            distanse_notify_check_in=self.env["ir.config_parameter"].get_param(
                str(self.env.user.company_id.id)
                + "hr_attendance_distanse_notify_check_in"
            )
        )
        res.update(
            distanse_notify_check_out=self.env["ir.config_parameter"].get_param(
                str(self.env.user.company_id.id)
                + "hr_attendance_distanse_notify_check_out"
            )
        )
        res.update(
            geotracking_batch_mode=self.env["ir.config_parameter"].get_param(
                str(self.env.user.company_id.id)
                + "hr_attendance_geotracking_batch_mode"
            )
        )
        res.update(
            geotracking_period_server_enable=self.env[
                "ir.config_parameter"
            ].get_param(
                str(self.env.user.company_id.id)
                + "hr_attendance_geotracking_period_server_enable"
            )
        )
        res.update(
            geotracking_period_server_qty=self.env[
                "ir.config_parameter"
            ].get_param(
                str(self.env.user.company_id.id)
                + "hr_attendance_geotracking_period_server_qty"
            )
        )
        return res
