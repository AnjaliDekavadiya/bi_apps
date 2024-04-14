from odoo import models, fields,api


class CustomerMeasurmets(models.Model):
    _name = "tailoring.customer.measurement"
    _description = "tailoring_customermeasurement"
    _rec_name = 'order_id'

    line_id = fields.Many2one("sale.order.line", string="Cart Line")
    customer_id = fields.Many2one('res.users',string="Customer")
    order_id = fields.Many2one('sale.order',string="Order ID")
    cloth_type = fields.Many2one('tailoring.cloth_type',string="Cloth type")
    measurement_ids = fields.One2many('tailoring.customer.measurement.inverse','measurement_id',string="Measurement")
    state = fields.Selection([('draft','DRAFT'),('confirmed','CONFIRMED')])


class CustomerMeasurmentsInverse(models.Model):
    _name = "tailoring.customer.measurement.inverse"
    _description = "tailoring_customer_measurement"

    measurement_id = fields.Many2one('tailoring.customer.measurement')
    name = fields.Char(string="Name")
    measures = fields.Float('measurements')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure',default=lambda self: self.env.ref('uom.product_uom_cm').id)


