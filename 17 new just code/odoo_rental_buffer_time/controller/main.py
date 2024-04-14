# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo.http import request
from odoo.addons.odoo_rental_request_management.controllers.main import CustomRentalSale


class CustomRentalSale(CustomRentalSale):

    def _prepare_buffer_domain_custom(self, kw, domain=[]):
        product_id = request.env['product.product'].sudo().browse(int(kw.get("product_id")))
        kw_start_datetime = self._convert_to_utc(kw.get("start_datetime"))
        kw_end_datetime = self._convert_to_utc(kw.get("end_datetime"))
        domain += [
            ('is_custom_rental_so_submitted', '=', True),
            ('product_id', '=', int(product_id.id)),
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

    def _check_rental_product_avail(self, kw, product_availability_dict):
        price_availability_dict = super(CustomRentalSale, self)._check_rental_product_avail(kw, product_availability_dict)
        if not price_availability_dict.get('reserved'):
            product_id = request.env['product.product'].sudo().browse(int(kw.get("product_id")))
            buffer_domain = self._prepare_buffer_domain_custom(kw, domain=[])
            buffer_time_ids = request.env['rental.custom.buffer.time'].search(buffer_domain)

            reserved_qty = sum(buffer_time_ids.mapped("reserved_qty")) or 0.0
            message = ''
            avail_rental_qty = product_id.custom_rental_qty - reserved_qty

            if avail_rental_qty < 0.0 or avail_rental_qty < float(kw.get("qty")):
                message += "%s Quantity is available" %(avail_rental_qty)
                product_availability_dict['availability_msg'] = message
                product_availability_dict['reserved'] = True
        return product_availability_dict

    def _submit_rental_quotation(self, kw):
        submit_quot_dict = super(CustomRentalSale, self)._submit_rental_quotation(kw)
        if submit_quot_dict.get("is_rental_quot_submitted") and submit_quot_dict.get("sale_order_id"):
            sale_order_id = submit_quot_dict.get("sale_order_id")
            sale_order_id.order_line._create_buffer_time_custom()
        return submit_quot_dict


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
