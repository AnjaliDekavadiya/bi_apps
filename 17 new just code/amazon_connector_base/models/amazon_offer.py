import json
import logging
import time
from xml.etree import ElementTree

from odoo import api, fields, models, _
from odoo.exceptions import UserError

from odoo.addons.sale_amazon import utils as amazon_utils


_logger = logging.getLogger(__name__)


class AmazonOffer(models.Model):
    _inherit = 'amazon.offer'
    _rec_name = "sku"

    @api.depends('sku', 'asin')
    def _compute_display_name(self):
        for product in self:
            product.display_name = f"{product.sku} - {product.asin or product.marketplace_id.name}"

    asin = fields.Char(string="ASIN")
    title = fields.Char(string="Title")
    display_name = fields.Char(
        compute='_compute_display_name', recursive=True, store=True, index=True
    )
    is_mfn = fields.Boolean("Manufacturer Fulfillment Network")
    is_afn = fields.Boolean("Amazon Fulfillment Network")
    parent_id = fields.Many2one(
        comodel_name="amazon.offer",
        string="Parent Product",
        compute="get_parent_product",
        store=True,
    )
    child_variant_ids = fields.One2many(
        comodel_name="amazon.offer",
        inverse_name="parent_id",
        string="Child Variants",
    )
    amazon_created_date = fields.Datetime(string="Created date on Amazon")
    amazon_issues = fields.Text(string="Issues JSON")
    data_json = fields.Text(string="Data JSON")

    @api.depends('product_template_id')
    def get_parent_product(self):
        for product in self:
            # if product.variation_data == 'child':
            #     continue
            main_product = product.product_template_id.product_variant_id
            parent_prod = self.search([
                ('product_id', '=', main_product.id),
                ('marketplace_id', '=', product.marketplace_id.id),
                # ('variation_data', '=', 'child'),
            ], limit=1)
            product.parent_id = parent_prod
    '''
    def export_stock_quantity(self, account, location, marketplace_ids=[]):
        def build_feed_messages(root_):
            """ Build the 'Message' elements to add to the feed.

            :param Element root_: The root XML element to which messages should be added.
            :return: None
            """
            for product_ in self.filtered(lambda p: p.is_mfn).mapped('product_id'):
                # Build the message base.
                odoo_prod = product_.with_context(location=location.id)
                message_ = ElementTree.SubElement(root_, 'Message')
                inventory_ = ElementTree.SubElement(message_, 'Inventory')
                ElementTree.SubElement(inventory_, 'SKU').text = odoo_prod.default_code
                stock_field = 'qty_available'
                if account.product_fbm_stock_field_id:
                    stock_field = account.product_fbm_stock_field_id.name
                quantity_ = int(odoo_prod[stock_field]) if odoo_prod[stock_field] > 0 else 0
                ElementTree.SubElement(inventory_, 'Quantity').text = str(quantity_)

        # amazon_utils.ensure_account_is_set_up(account)
        feed_env = self.env['feed.submission.log']

        xml_feed = amazon_utils.build_feed(account, 'Inventory', build_feed_messages)
        feed_env.with_context(no_submit=True).create({
            'account_id': account.id,
            'feed_message': xml_feed,
            'feed_type': 'POST_INVENTORY_AVAILABILITY_DATA',
            'amz_marketplace_ids': [(6, 0, marketplace_ids)],
        })
        return True'''

