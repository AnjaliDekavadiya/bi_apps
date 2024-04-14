# -*- coding: utf-8 -*-

from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    sale_cancel_custom_reason = fields.Text(
        string='Reason Details',
        copy=False,
        readonly=True,
    )
    so_cancel_reason_custom_id = fields.Many2one(
        'so.cancel.reason.custom',
        string='Reason',
        copy=False,
        readonly=True,
    )
    so_cancel_by_custom_id = fields.Many2one(
        'res.users',
        string='Cancelled By',
        readonly=True,
        copy=False,
    )
    so_cancel_custom_date = fields.Datetime(
        string='Cancelled Date',
        readonly=True,
        copy=False,
    )
    
    def action_cancel(self):
        if not self._context.get('custom_sale_cancel_wizard', False):
            action = self.env.ref('odoo_sale_cancel_reason.sale_order_cancel_custom_action').sudo().read()[0]
            return action
        else:
            return super(SaleOrder, self).action_cancel()
        return super(SaleOrder, self).action_cancel()
        