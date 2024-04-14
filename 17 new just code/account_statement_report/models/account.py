# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from odoo import models


class AccountAccount(models.Model):
    _inherit = "account.account"

    def get_move_lines(self, from_date, to_date):
        move_lines = self.env['account.move.line'].search(
            [
                ('account_id', '=', self.id),
                ('date', '>=', from_date),
                ('date', '<=', to_date)
            ], order='date')
        return move_lines
