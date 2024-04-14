from odoo import _, api, fields, models
from odoo.exceptions import UserError


class GenerateAmazonProductWizard(models.TransientModel):
    _name = "generate.amazon.product.wizard"

    amz_account_id = fields.Many2one(
        'amazon.account',
        string="Amazon Accounts",
        default=lambda self: self.env['amazon.account'].search([], limit=1),
        required=True
    )
    marketplace_ids = fields.Many2many(
        'amazon.marketplace',
        string="Marketplaces",
        domain="[('id', 'in', active_marketplace_ids)]",
        required=True
    )
    active_marketplace_ids = fields.Many2many(
        string="Account's Active Marketplaces",
        comodel_name='amazon.marketplace',
        related="amz_account_id.active_marketplace_ids",
    )
    is_mfn = fields.Boolean("Manufacturer Fulfillment Network")
    is_afn = fields.Boolean("Amazon Fulfillment Network")

    def button_export_amazon_middleware(self):
        products = self.env['product.product'].browse(self._context.get('active_ids'))
        if not products:
            return True
        if not self.marketplace_ids:
            raise UserError(_("Please choose at least one Marketplace!"))
        return products.generate_amazon_products(
            amz_account=self.amz_account_id,
            marketplaces=self.marketplace_ids,
            is_afn=self.is_afn,
            is_mfn=self.is_mfn
        )
