# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model_create_multi
    def create(self, vals_list):
        res_super = super(StockPicking, self).create(vals_list)
        for res in res_super:
            if res.user_id and self.env.company.sh_disable_follower_responsible_picking:
                res.message_unsubscribe([res.user_id.partner_id.id])
        return res_super

    def write(self, vals):
        if vals.get('user_id', False):
            user_id = self.env['res.users'].sudo().search(
                [('id', '=', vals.get('user_id', False))], limit=1)
            if user_id and self.env.company.sh_disable_follower_responsible_picking:
                res = super(StockPicking, self).write(vals)
                if self:
                    for rec in self:
                        rec.message_unsubscribe([user_id.partner_id.id])
                return res
        return super(StockPicking, self).write(vals)

    def message_subscribe(
            self,
            partner_ids=None,
            subtype_ids=None
    ):
        if self.env.company.sh_disable_follower_create_picking and not self.env.context.get('allow_manual_create') and not self.env.context.get('mail_invite_follower_channel_only') and not self.env.context.get('manually_added_follower'):
            return False
        elif self.env.context.get('allow_manual_create'):
            return super(StockPicking, self).message_subscribe(
                partner_ids, subtype_ids
            )
        else:
            return super(StockPicking, self).message_subscribe(
                partner_ids,
                subtype_ids
            )
        
    # for restrict to add user partner when validate transfer
    def button_validate(self):
        res=super(StockPicking,self).button_validate()

        if self.env.company.sh_disable_follower_responsible_picking :
            self.message_unsubscribe([self.env.user.partner_id.id])

        return res