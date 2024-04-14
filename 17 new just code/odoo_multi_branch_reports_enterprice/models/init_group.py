# -*- coding: utf-8 -*-

from odoo import models, api


class IRRule(models.Model):
    _inherit = "ir.rule"

    def init(self):
        (self.env.ref("odoo_multi_branch.account_move_company_branch_rules") + \
            self.env.ref("odoo_multi_branch.account_move_line_company_branch_rules") + \
            self.env.ref("odoo_multi_branch.account_bank_statement_company_branch_rules") + \
            self.env.ref("odoo_multi_branch.account_bank_statement_line_company_branch_rules")
            ).sudo().write({
            'groups' : [(4, self.env.ref('base.group_user').id)]
        })
