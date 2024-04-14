# -*- coding: utf-8 -*-

from odoo import models, fields, api
# from odoo.exceptions import Warning


class CancelPurchaseOrder(models.TransientModel):
    _name = "cancel.purchase.order"
    _description = 'Cancel Purchase Order'
    
    
    # @api.multi #odoo13
    def cancel_mass_purchase_order(self):
        active_ids = self._context.get("active_ids")
        purchase_order_ids = self.env['purchase.order'].browse(active_ids)
        if any(po.state == 'cancel' for po in purchase_order_ids):
            raise Warning("Selected Purchase Order is already cancelled")
        purchase_order_ids.button_cancel()
        action = self.env.ref("purchase.purchase_rfq").sudo().read()[0]
        action['domain'] = [('id', 'in', purchase_order_ids.ids)]
        return action
