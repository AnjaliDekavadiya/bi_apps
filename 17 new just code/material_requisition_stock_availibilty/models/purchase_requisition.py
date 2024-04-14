# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseRequisition(models.Model):
    _inherit = "material.purchase.requisition"

    #@api.multi
    def open_requisition_product_quants(self):
        self.ensure_one()
        #action = self.env.ref("stock.product_open_quants").sudo().read()[0]
        #action = self.env.ref("stock.product_open_quants").sudo().read()[0]
        action = self.env.ref("material_requisition_stock_availibilty.requisition_product_open_quants").sudo().read()[0]
        action['domain'] = [('product_id', 'in', self.requisition_line_ids.mapped('product_id').ids)]
        action['context'] = {'search_default_internal_loc': 1, 'search_default_productgroup': 1}
        return action
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
