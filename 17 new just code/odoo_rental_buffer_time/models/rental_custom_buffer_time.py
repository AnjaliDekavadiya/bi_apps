# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields
from odoo.exceptions import UserError


class RentalBufferTime(models.Model):
    _name = 'rental.custom.buffer.time'
    _description = 'Retal Buffer Time'
    _rec_name = 'sale_order_line_id'

    buffer_pickup_start_datetime = fields.Datetime(
        string="Buffer Start Time",
        required=True,
    )
    buffer_drop_end_datetime = fields.Datetime(
        string="Buffer End Time",
        required=True,
    )
    sale_order_line_id = fields.Many2one(
        'sale.order.line',
        string='Rental Order Line',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        related='sale_order_line_id.product_id',
        store=True,
    )
    reserved_qty = fields.Float(
        string='Quantity',
        related='sale_order_line_id.product_uom_qty',
        store=True,
    )
    is_custom_rental_so_submitted = fields.Boolean(
        string="Is Rental Submitted",
        copy=False,
        related="sale_order_line_id.is_custom_rental_so_submitted",
        store=True,
    )
    state = fields.Selection(
        selection=[
            ('confirm', 'Confirmed'),
            ('cancel', 'Cancelled'),
        ],
        string='State',
        default='confirm',
        copy=False,
    )

    def action_confirm_buffer_time(self):
        self.ensure_one()
        self.state = 'confirm'

    def action_cancel_buffer_time(self):
        self.ensure_one()
        self.state = 'cancel'

    def unlink(self):
        raise UserError(_("Do Not allow to delete buffer time entry, Please contact with you admin if you have any query."))
        return super(RentalBufferTime, self).unlink()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
