from odoo import models, fields,api,_


class Measurments(models.Model):
    _name = "tailoring.measurement"
    _description = "tailoring.measurement"

    name = fields.Char(string="Name", required=True)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure',default=lambda self: self.env.ref('uom.product_uom_cm').id)




class MeasurementRelative(models.Model):
    _name = "tailoring.measurement_relative"
    _description = "tailoring_measurement_relative"

    cloth_id = fields.Many2one('tailoring.cloth_type')
    measurement_id = fields.Many2one('tailoring.measurement', string="Name")
    uom_id = fields.Many2one(related="measurement_id.uom_id", string="Name")

    def _default_cloth_id(self):
        product = self.env['product.product'].browse(self.env.context.get('product_id'))
        if product:
            cloth_type = product.cloth_type
            return cloth_type
        
    # ...........................................Compute Measurement Name..........................................
    @api.depends('measurement_id')
    def _compute_measurement_name(self):
        for record in self:
            record.measurement_name = record.measurement_id.name
