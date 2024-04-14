# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    sh_membership_id = fields.Many2one(
        comodel_name="sh.parking.membership", string="Membership")


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    sh_card_no = fields.Char(string="Card no")
