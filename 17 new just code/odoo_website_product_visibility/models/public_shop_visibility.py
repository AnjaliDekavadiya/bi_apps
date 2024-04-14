# -*- coding: utf-8 -*-

# from openerp import models, fields, api, _
from odoo import models, fields, api, _ #odoo13
from odoo.exceptions import UserError


class PublicShopVisibility(models.Model):
    _name = "public.shop.visibility"
    _description = "Public Shop Visibility"

    name = fields.Char(
        string='Name',
        required=True,
    )
    all_category = fields.Boolean(
        string='Show All Category',
    )
    all_product = fields.Boolean(
        string='Show All Product'
    )
    category_ids = fields.Many2many(
        'product.public.category',
        string='Product Category',
    )
    template_ids = fields.Many2many(
        'product.template',
        string='Product Template',
    )

    @api.model
    def create(self, vals):
        visibility = self.search([])
        if visibility:
            raise UserError(_('Record already exist'))
        return super(PublicShopVisibility, self).create(vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
