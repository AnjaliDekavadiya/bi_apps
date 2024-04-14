# -*- coding: utf-8 -*-

# from openerp import models, fields
from odoo import models, fields #odoo13


class Partner(models.Model):
    _inherit = "res.partner"

    custom_visibility_category_ids = fields.Many2many(
        'product.public.category',
        string='Product Category',
    )
    custom_prob_template_ids = fields.Many2many(
        'product.template',
        string='Product Template',
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
