# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class BulkSaleOrderConfirm(models.TransientModel):
    _name = 'bulk.sale.order.confirm'
    _description = "Bulk Sale Order Confirm"

    is_confirm_sale = fields.Boolean(
        string="Are you sure to confirm sales order"
    )

    def confirm_sale_order(self):
        sale_order_ids = self.env['sale.order'].browse(self._context.get('active_ids', []))
        for rec in self:
            if rec.is_confirm_sale:
                if not all(order.state in ['draft', 'sent'] for order in sale_order_ids):
                    raise UserError(_("Please select 'quotation' and 'quotation sent' state sales order."))
                for order in sale_order_ids:
                    order.action_confirm()
                    order._send_order_confirmation_mail()