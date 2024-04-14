# -*- coding: utf-8 -*-

from odoo import fields, models, api
import werkzeug.urls


class ResCompany(models.Model):
    _inherit = "res.company"

    invoice_discount_product_id = fields.Many2one('product.product', string='Invoice Discount Product')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    invoice_discount_product_id = fields.Many2one('product.product', related='company_id.invoice_discount_product_id', string='Invoice Discount Product', readonly=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: