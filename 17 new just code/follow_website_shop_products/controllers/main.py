# -*- coding: utf-8 -*-
from odoo import http, fields
from odoo.http import request



class FollowWebsiteShopProducts(http.Controller):
    def _prepare_custom_follow_history(self,partner,product, post):
        vals = {
            'partner_id': partner,
            'product_id': product,
            'follow_time': fields.Date.today(),
        }
        return vals

    @http.route(['/follow/get/history_custom'], type='json', auth="user", methods=['POST'], website=True)
    def GetFollowHistoryCustom(self, **post):
        follow_btn = request.env['ir.ui.view']._render_template('follow_website_shop_products.product_follow_unfollow', values={
            'product': request.env['product.template'].browse(int(post.get('product_id'))),
            'website': request.env['website'].get_current_website(),
        })
        return {
            'follow_btn': follow_btn
        }

    @http.route(['/follow/history_custom'], type='json', auth="user", website=True)
    def FollowHistoryCustom(self, **post):

        follow_history_Obj = request.env['custom.follow.product.history'].sudo()
        vals = self._prepare_custom_follow_history(partner=int(post.get('partner_id')), product=int(post.get('product_id')), post=post)
        history = follow_history_Obj.sudo().create(vals)
        follow_btn = request.env['ir.ui.view']._render_template('follow_website_shop_products.product_follow_unfollow', values={
            'product': request.env['product.template'].browse(int(post.get('product_id'))),
            'website': request.env['website'].get_current_website(),
        })
        return {
            'follow_btn': follow_btn
        }

    @http.route(['/unfollow/history_custom'], type='json', auth="user", website=True)
    def UnfollowHistoryCustom(self, **post):
        if post.get('partner_id') and post.get('product_id'):
            history = request.env['custom.follow.product.history'].sudo().search([
                    ('partner_id', '=', int(post.get('partner_id'))),
                    ('active', '=', True),
                    ('product_id', '=', int(post.get('product_id'))),
                ])
            if history:
                history.write({
                    'unfollow_time': fields.Date.today(),
                    'active': False
                })
            follow_btn = request.env['ir.ui.view']._render_template('follow_website_shop_products.product_follow_unfollow', values={
                'product': request.env['product.template'].browse(int(post.get('product_id'))),
                'website': request.env['website'].get_current_website(),
            })
            return {
                'follow_btn': follow_btn
            }
        return {
                'follow_btn': False
            }
#        return True
