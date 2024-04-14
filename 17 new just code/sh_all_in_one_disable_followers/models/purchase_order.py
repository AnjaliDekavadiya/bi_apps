# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model_create_multi
    def create(self, vals_list):
        res_super = super(PurchaseOrder, self).create(vals_list)
        for res in res_super:
            if res.user_id and self.env.company.sh_disable_follower_pr_purchase:
                res.message_unsubscribe([res.user_id.partner_id.id])
        return res_super

    def write(self, vals):
        if vals.get('user_id', False):
            user_id = self.env['res.users'].sudo().search(
                [('id', '=', vals.get('user_id', False))], limit=1)
            if user_id and self.env.company.sh_disable_follower_pr_purchase:
                res = super(PurchaseOrder, self).write(vals)
                if self:
                    for rec in self:
                        rec.message_unsubscribe([user_id.partner_id.id])
                return res
        return super(PurchaseOrder, self).write(vals)

    def message_subscribe(self,
                          partner_ids=None,
                          subtype_ids=None
                          ):

        if self.env.company.sh_disable_follower_email and self.env.context.get('mark_rfq_as_sent') and not self.env.context.get('allow_manual_create') and not self.env.context.get('mail_invite_follower_channel_only'):

            return False

        elif self.env.company.sh_disable_follower_email and not self.env.context.get('mark_rfq_as_sent') and not self.env.context.get('allow_manual_create') and self.env.context.get('force_email') and not self.env.context.get('mail_invite_follower_channel_only'):

            return False

        elif self.env.company.sh_disable_follower_confirm_rfq and self.env.context.get('quotation_only') and not self.env.context.get('allow_manual_create') and not self.env.context.get('force_email'):

            return False

        else:
            return super(PurchaseOrder, self).message_subscribe(
                partner_ids, subtype_ids
            )
