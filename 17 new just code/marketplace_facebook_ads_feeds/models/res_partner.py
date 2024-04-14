# -*- coding: utf-8 -*-
################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
################################################################################


from odoo import _, api, fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    allow_seller_for_fb_ads = fields.Boolean(
        string='Allow Seller for facebook catalog integration',
        compute='_compute_allow_seller_for_fb_ads'
    )

    def _compute_allow_seller_for_fb_ads(self):
        for obj in self:
            obj.allow_seller_for_fb_ads = False
            seller_fb_ads_group = self.env.ref('marketplace_facebook_ads_feeds.group_for_mp_fb_ads_feeds')
            user_obj = self.env["res.users"].sudo().search([('partner_id', '=', obj.id)])
            user_groups = user_obj.read(['groups_id'])
            if user_groups and user_groups[0].get("groups_id"):
                user_groups_ids = user_groups[0].get("groups_id")
                if seller_fb_ads_group.id in user_groups_ids:
                    obj.allow_seller_for_fb_ads = True
            else:
                obj.allow_seller_for_fb_ads = False

    def enable_seller_fb_ads_group(self):
        for obj in self:
            user = self.env["res.users"].sudo().search(
                [('partner_id', '=', obj.id)])
            if user:
                group = self.env.ref('marketplace_facebook_ads_feeds.group_for_mp_fb_ads_feeds')
                if group:
                    group.sudo().write({"users": [(4, user.id, 0)]})

    def disable_seller_fb_ads_group(self):
        for obj in self:
            user = self.env["res.users"].sudo().search(
                [('partner_id', '=', obj.id)])
            if user:
                group = self.env.ref('marketplace_facebook_ads_feeds.group_for_mp_fb_ads_feeds')
                if group:
                    group.sudo().write({"users": [(3, user.id, 0)]})



    