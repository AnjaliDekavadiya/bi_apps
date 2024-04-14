from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends('display_type', 'company_id', 'move_id.ship_from_country_id')
    def _compute_account_id(self):
        country_dict = dict.fromkeys(
            self.mapped('move_id.ship_from_country_id').ids,
            self.env["account.move.line"]
        )
        country_dict[-1] = self.env["account.move.line"]
        for line in self:
            if (line.display_type not in ['product', 'line_section', 'line_note']
                or not line.move_id.ship_from_country_id.id):
                country_dict[-1] |= line
            else:
                country_dict[line.move_id.ship_from_country_id.id] |= line
        for country_id, lines in country_dict.items():
            if country_id == -1:
                super(AccountMoveLine, lines)._compute_account_id()
            else:
                super(AccountMoveLine, lines.with_context(origin_country_id=country_id)
                      )._compute_account_id()

    def _get_computed_taxes(self):
        self.ensure_one()
        country = self.move_id.ship_from_country_id
        if not country:
            return super()._get_computed_taxes()
        if self.move_id.is_sale_document(include_receipts=True):
            # Out invoice.
            if self.product_id.taxes_id:
                tax_ids = self.product_id.taxes_id.filtered(lambda tax: tax.company_id == self.move_id.company_id)
            else:
                tax_ids = self.account_id.tax_ids.filtered(lambda tax: tax.type_tax_use == 'sale')
            if not tax_ids and self.display_type == 'product':
                tax_ids = self.move_id.company_id.account_sale_tax_id
        elif self.move_id.is_purchase_document(include_receipts=True):
            # In invoice.
            if self.product_id.supplier_taxes_id:
                tax_ids = self.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == self.move_id.company_id)
            else:
                tax_ids = self.account_id.tax_ids.filtered(lambda tax: tax.type_tax_use == 'purchase')
            if not tax_ids and self.display_type == 'product':
                tax_ids = self.move_id.company_id.account_purchase_tax_id
        else:
            # Miscellaneous operation.
            tax_ids = self.account_id.tax_ids

        if self.company_id and tax_ids:
            tax_ids = tax_ids.filtered(lambda tax: tax.company_id == self.company_id)

        if tax_ids and self.move_id.fiscal_position_id:
            tax_ids = self.move_id.fiscal_position_id.with_context(
                origin_country_id=country.id
            ).map_tax(tax_ids)

        return tax_ids
