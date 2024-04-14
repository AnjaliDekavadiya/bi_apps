import logging
import pprint
from datetime import datetime
from xml.etree import ElementTree

from odoo import api, fields, models, _
from odoo.exceptions import UserError

from odoo.addons.sale_amazon import utils as amazon_utils


class ProductProduct(models.Model):
    _inherit = 'product.product'


    def export_stock_quantity(self, account, location, marketplaces):
        def build_feed_messages(root_):
            """ Build the 'Message' elements to add to the feed.

            :param Element root_: The root XML element to which messages should be added.
            :return: None
            """
            for product_ in self.filtered(lambda p: p.default_code):
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
            'amz_marketplace_ids': [(6, 0, marketplaces.ids)],
        })
        return True

    def generate_amazon_products(self, amz_account, marketplaces,
                                 is_afn=False, is_mfn=False):
        amz_product_env = self.env['amazon.offer']
        vals_list = []
        for mp in marketplaces:
            for product in self:
                existed_product = amz_product_env.search([
                    ('account_id', '=', amz_account.id),
                    ('marketplace_id', '=', mp.id),
                    ('product_id', '=', product.id),
                ])
                if existed_product:
                    existed_product.write({
                    #     'sku': product.default_code,
                        'is_afn': is_afn,
                        'is_mfn': is_mfn,
                    })
                    continue
                vals = {
                    'account_id': amz_account.id,
                    'marketplace_id': mp.id,
                    'product_id': product.id,
                    'sku': product.default_code,
                    'is_afn': is_afn,
                    'is_mfn': is_mfn,
                }
                vals_list.append(vals)
        amz_products = amz_product_env.create(vals_list)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Amazon Products'),
            'res_model': 'amazon.offer',
            'view_mode': 'tree',
            'domain': [('id', 'in', amz_products.ids)],
        }
