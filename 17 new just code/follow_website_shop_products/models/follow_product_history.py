# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class CustomFollowProductHistory(models.Model):
    _name = 'custom.follow.product.history'
    _description = 'Custom Follow Product History'
    _rec_name = 'product_id'

    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
    )

    product_id = fields.Many2one(
        'product.template',
        string='Product',
    )
    active = fields.Boolean('Active',
        default=True,
        store=True,
        readonly=False
    )

    follow_time = fields.Date(
        string="Follow Date",
        copy=False,
    )

    unfollow_time = fields.Date(
        string="Unfollow Date",
        copy=False,
    )
    def follow_check(self,product, partner):
        history = self.env['custom.follow.product.history'].sudo().search([
#                ('partner_id', '=', partner),
                ('partner_id', '=', int(partner)),
                ('active', '=', True),
                ('product_id', '=', int(product))
#                ('product_id', '=', product)
            ])
        if not history:
            return False
        return True
