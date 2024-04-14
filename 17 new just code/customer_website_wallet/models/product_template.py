# -*- coding: utf-8 -*-

#from openerp import models, fields, api
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_wallet_product = fields.Boolean(
        string= "Is Wallet Product",
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
