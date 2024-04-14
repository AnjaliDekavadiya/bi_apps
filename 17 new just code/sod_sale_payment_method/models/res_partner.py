# Copyright 2019-2023 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_payment_method_id = fields.Many2one(
        "account.journal",
        domain=[("type", "in", ["bank", "cash"])],
        string="Sale Payment Method",
        copy=False,
    )
