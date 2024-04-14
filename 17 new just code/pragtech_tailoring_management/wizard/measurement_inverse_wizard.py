from odoo import models, fields, api


class MeasurementWizardLine(models.TransientModel):
    _name = 'measurement.wizard.line'
    _description = 'Measurement Wizard Line'

    wizard_id = fields.Many2one('measurement.wizard', string="Wizard")
    measurement_id = fields.Many2one('tailoring.measurement', string="Measurement")
    measure = fields.Float('measures')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure',default=lambda self: self.env.ref('uom.product_uom_cm').id)
    
