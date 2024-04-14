'''
Created on Sep 18, 2018

@author: Zuhair Hammadi
'''
from odoo import models, api, _

class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = ['approval.record', 'purchase.order']
    
    @api.model
    def _before_approval_states(self):
        return [('draft', _('RFQ')),('sent', _('RFQ Sent'))]
    
    @api.model
    def _after_approval_states(self):
        return [('purchase', _('Purchase Order')), ('done', _('Locked')), ('rejected', _('Rejected')), ('cancel', _('Cancelled'))]    

    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order.order_line._validate_analytic_distribution()
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.action_approve()
            else:
                continue
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True
    
    def button_cancel(self):
        self._remove_approval_activity()
        return super(PurchaseOrder, self).button_cancel()    
    
    def _approval_allowed(self):
        return self.user_can_approve
    
    def _on_approve(self):
        self.button_approve()