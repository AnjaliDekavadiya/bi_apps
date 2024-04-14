from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"
    
    passengers_ids = fields.One2many('fleet.passengers','vehicle_id','Passengers')

    @api.constrains('driver_id')
    def _check_driver_id(self):
        for rec in self:
            active = self.env['fleet.vehicle'].search_count([('driver_id', '=', rec.driver_id.id)])
            if active > 1:
                raise ValidationError("Driver is already assigned for a vehicle !")