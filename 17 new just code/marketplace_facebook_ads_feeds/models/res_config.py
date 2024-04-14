# -*- coding: utf-8 -*-
################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
################################################################################


from odoo import _, api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_allow_seller_for_fb_ads = fields.Boolean(
        string='Enable to allow Seller for facebook catalog integration',
        group= 'odoo_marketplace.marketplace_seller_group',
        implied_group='marketplace_facebook_ads_feeds.group_for_mp_fb_ads_feeds'
    )

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.default'].sudo().set('res.config.settings', 'group_allow_seller_for_fb_ads', self.group_allow_seller_for_fb_ads)
        return True


    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        group_allow_seller_for_fb_ads = self.env['ir.default'].sudo()._get(
            'res.config.settings', 'group_allow_seller_for_fb_ads')
        res.update({
            'group_allow_seller_for_fb_ads':group_allow_seller_for_fb_ads,
        })
        return res
