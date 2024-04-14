# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model_create_multi
    def create(self, vals_list):
        res_super = super(SaleOrder, self).create(vals_list)
        for res in res_super:
            if res.user_id and self.env.company.sh_disable_follower_salesperson:
                res.message_unsubscribe([res.user_id.partner_id.id])
        return res_super

    def write(self, vals):
        if vals.get('user_id', False):
            user_id = self.env['res.users'].sudo().search(
                [('id', '=', vals.get('user_id', False))], limit=1)
            if user_id and self.env.company.sh_disable_follower_salesperson:
                res = super(SaleOrder, self).write(vals)
                if self:
                    for rec in self:
                        rec.message_unsubscribe([user_id.partner_id.id])
                return res
        return super(SaleOrder, self).write(vals)

    def message_subscribe(
        self,
        partner_ids=None,
        subtype_ids=None
    ):
        if self.env.company.sh_disable_follower_email and self.env.context.get('mark_so_as_sent') and not self.env.context.get('allow_manual_create') and not self.env.context.get('mail_invite_follower_channel_only') and not self.env.context.get('manually_added_follower'):
            return False
        elif self.env.company.sh_disable_follower_confirm_sale and not self.env.context.get('mark_so_as_sent') and not self.env.context.get('allow_manual_create') and not self.env.context.get('mail_invite_follower_channel_only') and not self.env.context.get('manually_added_follower'):
            return False
        elif self.env.context.get('allow_manual_create'):
            return super(SaleOrder, self).message_subscribe(
                partner_ids, subtype_ids
            )
        else:
            return super(SaleOrder, self).message_subscribe(
                partner_ids, subtype_ids
            )
