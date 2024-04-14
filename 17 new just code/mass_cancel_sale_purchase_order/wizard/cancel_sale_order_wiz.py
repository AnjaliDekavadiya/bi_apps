# -*- coding: utf-8 -*-

from odoo import models, fields, api
# from odoo.exceptions import Warning


class CancelSaleOrder(models.TransientModel):
    _name = "cancel.sale.order"
    _description = 'Cancel Sale Order'
    
    
    # @api.multi #odoo13
    def cancel_mass_sale_order(self):
        active_ids = self._context.get("active_ids")
        sale_order_ids = self.env['sale.order'].browse(active_ids)
        # sale_order_ids.action_cancel()
        sale_order_ids._action_cancel()
        action = self.env.ref("sale.action_quotations_with_onboarding").sudo().read()[0]
        action['domain'] = [('id', 'in', sale_order_ids.ids)]
        return action
