# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HelpdeskSupport(models.Model):
    _inherit = 'helpdesk.support'

    cust_pos_order_id = fields.Many2one(
        'pos.order',
        string="POS Order",
        copy=False,
    )

    def show_helpdesk_pos_custom(self):
        self.ensure_one()
        res = self.env.ref('point_of_sale.action_pos_pos_form')
        res = res.sudo().read()[0]
        res['domain'] = str([('id','in',self.cust_pos_order_id.ids)])
        return res

    @api.model
    def create(self, vals):
        context = self._context.copy()
        if context.get('post'):
            if context['post'].get('helpdesk_pos_order_id'):
                vals.update({'cust_pos_order_id': context['post'].get('helpdesk_pos_order_id')})
        return super(HelpdeskSupport, self).create(vals)