# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Partner(models.Model):
    _inherit ="res.partner"
    
    rma_order_count = fields.Integer(
        compute="_rma_order_count",
    )
    
#    @api.multi odoo13
    @api.depends()
    def _rma_order_count(self):
        for rec in self:
            rec.rma_order_count = self.env['return.order'].search_count([
                        ('partner_id', 'child_of', rec.id),
            ])
    
#    @api.multi odoo13
    def action_view_return_rma(self):
        for rec in self:
            rma_order_id = self.env['return.order'].search([
                        ('partner_id', 'child_of', rec.id),
            ])
        # action = self.env.ref('website_shop_return_rma.action_return_rma')
        # result = action.sudo().read()[0]
        result = self.env["ir.actions.actions"]._for_xml_id("website_shop_return_rma.action_return_rma")
        result['domain'] = [('id', 'in', rma_order_id.ids)]
        return result
