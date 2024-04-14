# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime, date


class SubcontractPO(models.TransientModel):
    _name = 'subcontract.purchase.order'
    _description = 'Subcontract purchase Order'

    user_id = fields.Many2one('res.partner','Vendor/Sub Contractor', required=True)
    
    def create_po_from_subc(self):
        subcontracts = self.env['job.subcontract'].browse(self._context.get('active_ids', []))
        
        po_obj = self.env['purchase.order']
        po_line_obj = self.env['purchase.order.line']
        
        po_id = po_obj.create({'partner_id': self.user_id.id, 'date_planned': datetime.now(), 'subcontract_id': subcontracts.id})
        
        for po_line in subcontracts.purchase_line_ids:
           po_line_obj.create({
                'product_id': po_line.product_id.id,
                'name': po_line.product_id.name,
                'product_qty': po_line.qty,
                'price_unit': po_line.product_id.lst_price,
                'date_planned': datetime.now(),
                'product_uom': po_line.uom_id.id,
                'order_id': po_id.id,
                
                
                
           }) 
        
        
        
        
        
