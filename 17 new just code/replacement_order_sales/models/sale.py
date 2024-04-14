# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    replacement_reason_custom_id = fields.Many2one(
        'replacement.reason.custom',
        string='Replacement Reason',
        copy=False,
        readonly=False,
    )
    replacement_custom_name = fields.Char(
        string='Replacement Number',
        readonly=True,
        copy=False,
    )
    replacement_custoriginal_salesorder_id = fields.Many2one(
        'sale.order',
        string='Original Sale Order',
        copy=False,
    )

    @api.model
    def create(self, vals):
        if self.env.context.get('default_is_replacement_custom'):
            vals['name'] = 'Replacement Order'
            vals['replacement_custom_name'] = self.env['ir.sequence'].next_by_code('replacement.order.custom') or _('New')
        return super(SaleOrder, self).create(vals)

    def action_custom_replacement_so(self):
        self.ensure_one()
        res = self.env.ref('replacement_order_sales.action_replacement_order_custom')
        res = res.sudo().read()[0]
        res['domain'] = str([('replacement_custoriginal_salesorder_id','=',self.id)])
        return res

    
            
    