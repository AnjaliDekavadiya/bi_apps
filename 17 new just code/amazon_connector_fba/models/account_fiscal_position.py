from odoo import fields, models
from odoo.exceptions import UserError


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    def map_tax(self, taxes):
        # result = super().map_tax(taxes)
        if not self.env.context.get("origin_country_id"):
            #return result
            origin_country_id = False
        else:
            origin_country_id = self.env.context["origin_country_id"]
        result = self.env["account.tax"]
        tax_candidates = self.tax_ids.filtered(
            lambda t: t.origin_country_id.id == origin_country_id)
        if not tax_candidates:
            tax_candidates = self.tax_ids.filtered(lambda t: not t.origin_country_id)
        for tax in taxes:
            taxes_correspondance = tax_candidates.filtered(
                lambda t: t.tax_src_id == tax._origin
            )
            if taxes_correspondance:
                result |= taxes_correspondance.tax_dest_id
        if not result:
             return super().map_tax(taxes)
        return result

    def map_account(self, account):
        # result = super().map_account(account)
        if not self.env.context.get("origin_country_id"):
            #return result
            origin_country_id = False
        else:
            origin_country_id = self.env.context["origin_country_id"]
        for pos in self.account_ids:
            if (pos.account_src_id == account and pos.origin_country_id.id ==
                origin_country_id):
                return pos.account_dest_id
        return super().map_account(account)

    def map_accounts(self, accounts):
        # result = super().map_accounts(accounts)
        if not self.env.context.get("origin_country_id"):
            #return result
            origin_country_id = False
        else:
            origin_country_id = self.env.context["origin_country_id"]
        ref_dict = {}
        positions = self.account_ids.filtered(
            lambda l: l.origin_country_id.id == origin_country_id)
        if not positions:
            positions = self.account_ids.filtered(lambda l: not l.origin_country_id)
        for line in positions:
            ref_dict[line.account_src_id] = line.account_dest_id
        for key, acc in accounts.items():
            if acc in ref_dict:
                accounts[key] = ref_dict[acc]
        return accounts


class AccountFiscalPositionTax(models.Model):
    _inherit = "account.fiscal.position.tax"

    origin_country_id = fields.Many2one("res.country", string="Origin Country")

    _sql_constraints = [
        ('tax_src_dest_uniq',
         'unique (position_id,tax_src_id,tax_dest_id,origin_country_id)',
         'A tax fiscal position could be defined only one time on same taxes.')
    ]


class AccountFiscalPositionAccount(models.Model):
    _inherit = "account.fiscal.position.account"

    origin_country_id = fields.Many2one("res.country", string="Origin Country")

    _sql_constraints = [
        ('account_src_dest_uniq',
         'unique (position_id,account_src_id,account_dest_id,origin_country_id)',
         'An account fiscal position could be defined only one time on same accounts.')
    ]
