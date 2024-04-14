from odoo import models, fields, api
from odoo.exceptions import ValidationError

class assigningMeasurementWizard(models.TransientModel):
    _name = 'measurement.wizard'
    _description = 'measurement_wizard'

    order_id = fields.Many2one("sale.order")
    measurment_name_id = fields.Many2one('tailoring.measurement')
    cloth_category_id = fields.Many2one('tailoring.cloth_type')
    measurement_lines_ids = fields.One2many('measurement.wizard.line', 'wizard_id', string="Measurements")


    def default_get(self, vals):
        res = super(assigningMeasurementWizard, self).default_get(vals)
        # Check if 'cloth_category_id' is a valid integer value
        cloth_category_id = res.get('cloth_category_id')

        if isinstance(cloth_category_id, int):
            list_measurement = []
            from_cloth_table = self.env['tailoring.cloth_type'].browse(cloth_category_id)
            for rec in from_cloth_table.measurement_ids:
                vals = {
                    'measurement_id': rec.measurement_id.id
                }
                list_measurement.append((0, 0, vals))

            res.update({'measurement_lines_ids': list_measurement})

        return res


    def measurement_assign_action(self):
        CustomerMeasurement = self.env['tailoring.customer.measurement']
        SaleOrderLine = self.env['sale.order.line']
        saleorder = self.env['sale.order']

        list1 = []
        measurement_dict = {
            'order_id': self.order_id.id,
            'cloth_type': self.cloth_category_id and self.cloth_category_id.id or False
        }

        # Iterate through the measurement lines and create CustomerMeasurement records
        for line in self.measurement_lines_ids:
            if not line.measure:
                raise ValidationError("Measure field should not be empty.")
            measurement_values = {
                'name': line.measurement_id.name,
                'measures': line.measure,
                'uom_id': line.uom_id.id,
            }
            list1.append((0, 0, measurement_values))

        measurement_dict.update({'measurement_ids': list1})
        CustomerMeasurement.create(measurement_dict)

        # Update the 'done' field in SaleOrderLine to True
        sale_order_lines = SaleOrderLine.search([
            ('order_id', '=', self.order_id.id),
            ('cloth_type_id', '=', self.cloth_category_id.id)
        ])
        sale_order = saleorder.search([('done', '=', False)])
        sale_order_lines.write({'done': True})
        sale_order.write({'done': True})
        return {'type': 'ir.actions.act_window_close'}
    
