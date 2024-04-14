# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    wk_is_gift_card = fields.Boolean(
        string='Is Gift Card')

    wk_validity = fields.Integer(
        string="Validity",
        default="1",
    )
    wk_validity_unit = fields.Selection(
        [('months', 'Months'), ('years', 'Years')],
        default="years",
        string="Validity Unit")
    wk_is_partially_redemed = fields.Boolean(
        string='Use Partial Redemption',
        default=True,
        help="Enable this option partial redemption option.")
    wk_redeemption_limit = fields.Integer(
        string='Max Redemption Limit',
        default=1,
        help="The maximum number of times the coupon can be redeemed. -1 means the coupon can be used any number of times untill the voucher value is Zero.")

    wk_use_minimum_cart_value = fields.Boolean(
        string='Use Minimum Cart Value',
        default=False
    )

    wk_minimum_cart_value = fields.Float(
        string='Minimum Cart Amount',
        default=1000
    )

    @api.constrains('wk_validity', 'wk_is_gift_card', 'list_price', 'wk_redeemption_limit', 'wk_is_partially_redemed', 'taxes_id', 'supplier_taxes_id')
    def check_all(self):
        for record in self:
            if record.wk_is_gift_card:
                IrDefault = self.env['ir.default'].sudo()._get
                if record.wk_validity <= 0:
                    raise ValidationError(
                        ('Validity must be greater than zero'))
                if record.list_price > IrDefault('res.config.settings', 'wk_coupon_max_amount'):
                    raise ValidationError(('You can`t create gift greater than this maximum amount (%s) !!!') % IrDefault.get(
                        'res.config.settings', 'wk_coupon_max_amount'))
                if record.list_price <= 0:
                    raise ValidationError(('GIft Card Value cannot be <= 0.'))
                if record.wk_is_partially_redemed and record.wk_redeemption_limit <= 0:
                    raise ValidationError(
                        ('Reedemption limit must be greater than zero'))

    @api.onchange('wk_is_gift_card',)
    def change_wk_is_gift_card(self):
        pos_gift_cart_categ = self.env.ref(
            'wk_pos_gift_card.wk_pos_gift_card_categ')
        if self.wk_is_gift_card:
            self.available_in_pos = True
            self.pos_categ_ids = pos_gift_cart_categ.ids
        elif self.pos_categ_ids and self.pos_categ_ids.ids == pos_gift_cart_categ.id:
            self.pos_categ_ids = False

    @api.onchange('pos_categ_id')
    def change_pos_categ_of_gift_card(self):
        pos_gift_cart_categ = self.env.ref(
            'wk_pos_gift_card.wk_pos_gift_card_categ')
        if self.pos_categ_id and self.pos_categ_id.ids == pos_gift_cart_categ.id:
            self.wk_is_gift_card = True
        else:
            self.pos_categ_id = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('taxes_id'):
                vals['taxes_id'] = None
            if vals.get('supplier_taxes_id'):
                vals['supplier_taxes_id'] = None
        return super(ProductTemplate, self).create(vals_list)
