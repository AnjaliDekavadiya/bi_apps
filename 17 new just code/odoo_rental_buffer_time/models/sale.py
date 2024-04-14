# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, _
from datetime import datetime, timedelta


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_submit_rental_order_custom(self):
        res = super(SaleOrder, self).action_submit_rental_order_custom()
        self.order_line._create_buffer_time_custom()

    def action_unreserve_rental_order_custom(self):
        res = super(SaleOrder, self).action_unreserve_rental_order_custom()
        self.order_line.mapped('custom_buffer_time_id').write({
            'state': 'cancel',
        })

    def action_view_custom_rental_buffer_time(self):
        action=self.env.ref("odoo_rental_buffer_time.action_custom_buffer_time_report").sudo().read()[0]
        action['domain'] = [('id', 'in', self.order_line.mapped('custom_buffer_time_id').ids)]
        return action

    def unlink(self):
        self.order_line.mapped('custom_buffer_time_id').write({
            'state': 'cancel',
        })
        res = super(SaleOrder, self).unlink()
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    custom_buffer_time_id = fields.Many2one(
        'rental.custom.buffer.time',
        string='Rental Buffer Time',
        copy=False,
        # readonly="1"
        readonly=True
    )
    buffer_pickup_start_datetime = fields.Datetime(
        string="Buffer Start Time",
        related='custom_buffer_time_id.buffer_pickup_start_datetime',
        copy=False,
        # readonly="1"
        readonly=True
    )
    buffer_drop_end_datetime = fields.Datetime(
        string="Buffer End Time",
        related='custom_buffer_time_id.buffer_drop_end_datetime',
        copy=False,
        # readonly="1"
        readonly=True
    )

    def _prepare_buffer_domain_custom(self, domain=[]):
        kw_start_datetime = self.custom_start_datetime
        kw_end_datetime = self.custom_end_datetime
        domain += [
            ('is_custom_rental_so_submitted', '=', True),
            ('product_id', '=', self.product_id.id),
            '|', '|', '&', 
            ('buffer_pickup_start_datetime', '>=', kw_start_datetime),
            ('buffer_pickup_start_datetime', '<=', kw_end_datetime),
            '&',
            ('buffer_drop_end_datetime', '>=', kw_start_datetime),
            ('buffer_drop_end_datetime', '<=', kw_end_datetime),
            '&',
            ('buffer_pickup_start_datetime', '<=', kw_start_datetime),
            ('buffer_drop_end_datetime', '>=', kw_end_datetime)
        ]
        return domain

    def _check_rental_product_avail_custom(self):
        self.ensure_one()
        price_availability_dict = super(SaleOrderLine, self)._check_rental_product_avail_custom()
        if not price_availability_dict.get('reserved'):
            product_id = self.product_id
            buffer_domain = self._prepare_buffer_domain_custom(domain=[])
            buffer_time_ids = self.env['rental.custom.buffer.time'].search(buffer_domain)

            if buffer_time_ids:
                reserved_qty = sum(buffer_time_ids.mapped("reserved_qty")) or 0.0
                message = ''
                avail_rental_qty = product_id.custom_rental_qty - reserved_qty

                if avail_rental_qty < float(self.product_uom_qty):
                    message += "%s Quantity is available" %(avail_rental_qty)
                    price_availability_dict['availability_msg'] = message
                    price_availability_dict['reserved'] = True
        return price_availability_dict

    def _prepare_custom_buffer_time_vals(self, line):
        start_buffer_time = line.product_id.custom_buffer_pickup_time
        end_buffer_time = line.product_id.custom_buffer_drop_time
        buffer_pickup_start_datetime = line.custom_start_datetime - timedelta(hours=start_buffer_time)
        buffer_drop_end_datetime = line.custom_end_datetime + timedelta(hours=end_buffer_time)
        return {
            'buffer_pickup_start_datetime': buffer_pickup_start_datetime,
            'buffer_drop_end_datetime': buffer_drop_end_datetime,
            'sale_order_line_id': line.id,
        }

    def _create_buffer_time_custom(self):
        lines = self
        for line in lines:
            if line.order_id.is_custom_rental_quote and line.product_id.product_tmpl_id.custom_rental_product and line.custom_start_datetime and line.custom_end_datetime:
                if line.custom_buffer_time_id and line.custom_buffer_time_id.state != 'confirm':
                    line.custom_buffer_time_id.write({
                        'state': 'confirm'
                    })
                else:
                    custom_buffer_time_vals = self._prepare_custom_buffer_time_vals(line)
                    buffer_time_id = self.env['rental.custom.buffer.time'].create(custom_buffer_time_vals)
                    line.custom_buffer_time_id = buffer_time_id.id
        return lines

    def unlink(self):
        self.mapped('custom_buffer_time_id').write({
            'state': 'cancel',
        })
        res = super(SaleOrderLine, self).unlink()
        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
