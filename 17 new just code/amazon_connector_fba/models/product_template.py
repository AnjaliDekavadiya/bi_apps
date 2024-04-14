from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def get_product_accounts(self, fiscal_pos=None):
        origin_country_id = self.env.context.get("origin_country_id")
        if fiscal_pos and origin_country_id:
            fiscal_pos = fiscal_pos.with_context(origin_country_id=origin_country_id)
        return super().get_product_accounts(fiscal_pos=fiscal_pos)
