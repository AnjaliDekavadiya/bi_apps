# Copyright 2020-2023 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import fields, models


class PartnerCreditLimit(models.TransientModel):
    _name = "partner.credit.limit.warning"
    _description = "Credit Warnings"

    message = fields.Text(readonly=True)
