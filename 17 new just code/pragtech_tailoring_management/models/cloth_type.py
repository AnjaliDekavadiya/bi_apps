from odoo import models, fields, api , _

class ClothType(models.Model):
    _name = 'tailoring.cloth_type'
    _description = 'tailoring_cloth_type'

    name = fields.Char(string = 'Cloth Name',required=True)
    fabric_id = fields.Many2one('tailoring.fabric',string = 'Fabric')
    measurement_ids = fields.One2many('tailoring.measurement_relative', 'cloth_id',string = 'Measurement')

    def get_measurements(self):
        measurements = []
        for measurement in self.measurement_ids:
            measurements.append({
                'measurement_name': measurement.measurement_name,
                'measurement_value': measurement.measurement_value,
            })
        return measurements