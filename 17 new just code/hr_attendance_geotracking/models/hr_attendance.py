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

from pyproj import Proj, transform
from shapely.geometry import LineString, Point

from odoo import api, fields, models


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    geo_coords_ids = fields.One2many(
        "hr.attendance.geo.coords",
        "hr_attendance_id",
        string="Geo coords table",
        readonly=True,
    )
    geo_tracking = fields.GeoLine(
        "Geo tracking", compute="_compute_geo_tracking", store=True
    )

    @api.depends("geo_coords_ids.point")
    def _compute_geo_tracking(self):
        P3857 = Proj(init="epsg:3857")
        P4326 = Proj(init="epsg:4326")
        for rec in self:
            coords = []
            for track in rec.geo_coords_ids:
                x, y = transform(P4326, P3857, track.longitude, track.latitude)
                coords.append(Point(x, y))
            if len(coords):
                rec.geo_tracking = LineString(
                    coords * 2 if len(coords) == 1 else coords
                )


class HrAttendanceGeoCoords(models.Model):
    _name = "hr.attendance.geo.coords"

    latitude = fields.Char(string="Latitude of location")
    longitude = fields.Char(string="Longitude of location")
    point = fields.GeoPoint(
        "Geo point", compute="_compute_geo_point", store=True
    )
    hr_attendance_id = fields.Many2one("hr.attendance", string="Attendance")
    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env.user.company_id.id,
    )

    @api.depends("latitude", "longitude")
    def _compute_geo_point(self):
        P3857 = Proj(init="epsg:3857")
        P4326 = Proj(init="epsg:4326")
        for rec in self:
            if rec.latitude and rec.longitude:
                x, y = transform(P4326, P3857, rec.longitude, rec.latitude)
                rec.point = Point(x, y)
