# -*- coding: utf-8 -*-

from odoo import models, api

class MaterialPurchaseRequisition(models.Model):
    _inherit = 'material.purchase.requisition'
    
    @api.model
    def _prepare_pick_vals(self, line=False, stock_id=False):
        res = super(MaterialPurchaseRequisition, self)._prepare_pick_vals(line=line, stock_id=stock_id)
        res.update({
            'car_repair_request_id' : self.custom_car_repair_id.id,
            'car_repaircustom_task_id' : self.custom_task_id.id,
            })
        return res
        
    # @api.multi #odoo13
    def request_stock(self):
        res = super(MaterialPurchaseRequisition, self).request_stock()
        for rec in self:
            purchase_order_ids = self.env['purchase.order'].search([('custom_requisition_id', '=', rec.id)])
            purchase_order_ids.write({
                'car_repair_id' : rec.custom_car_repair_id.id,
            })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
