import json
import logging

import dateutil.parser
import pprint

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.addons.sale_amazon import utils as amazon_utils

_logger = logging.getLogger(__name__)
FEED_BULK_RECORD_LIMIT_RATE = 999


class AmazonAccount(models.Model):
    _inherit = 'amazon.account'

    use_amz_ref_so_number = fields.Boolean(
        string="Use Amazon Order as SO Number", default=True,
        help="If checked, the Amazon Order Reference will be used as the SO Number."
    )
    is_keeping_order_draft = fields.Boolean(
        string="Keep Amazon Order as Draft",
        default=False,
        help="If checked, the order will be kept as draft instead of being set to sale."
    )
    product_fbm_stock_field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        domain=[('model', '=', 'product.product'), ('ttype', '=', 'float')]
    )

    def _find_or_create_partners_from_data(self, order_data):
        contact, delivery = super()._find_or_create_partners_from_data(order_data)
        marketplace = self.env['amazon.marketplace'].search([
            ('api_ref', '=', order_data['MarketplaceId'])
        ])
        if marketplace.account_id and marketplace.account_id != contact.property_account_receivable_id:
            contact.write({'property_account_receivable_id': marketplace.account_id.id})
            # delivery.write({'property_account_receivable_id': marketplace.account_id.id})
        return contact, delivery

    def _create_order_from_data(self, order_data):
        """ Create a new sales order based on the provided order data.

        Note: self.ensure_one()

        :param dict order_data: The order data to create a sales order from.
        :return: The newly created sales order.
        :rtype: record of `sale.order`
        """
        self.ensure_one()

        # Prepare the order line values.
        shipping_code = order_data.get('ShipServiceLevel')
        shipping_product = self._find_matching_product(
            shipping_code, 'shipping_product', 'Shipping', 'service'
        )
        currency = self.env['res.currency'].with_context(active_test=False).search(
            [('name', '=', order_data['OrderTotal']['CurrencyCode'])], limit=1
        )
        amazon_order_ref = order_data['AmazonOrderId']
        contact_partner, delivery_partner = self._find_or_create_partners_from_data(order_data)
        fiscal_position = self.env['account.fiscal.position'].with_company(
            self.company_id
        )._get_fiscal_position(contact_partner, delivery_partner)
        order_lines_values = self._prepare_order_lines_values(
            order_data, currency, fiscal_position, shipping_product
        )

        # Create the sales order.
        fulfillment_channel = order_data['FulfillmentChannel']
        # The state is first set to 'sale' and later to 'done' to generate a picking if fulfilled
        # by merchant, or directly set to 'done' to generate no picking if fulfilled by Amazon.
        # ----------- OVERRIDE -----------
        state = 'draft' if fulfillment_channel == 'AFN' else 'sale'
        # ----------- END OVERRIDE -----------
        purchase_date = dateutil.parser.parse(order_data['PurchaseDate']).replace(tzinfo=None)
        order_vals = {
            'origin': f"Amazon Order {amazon_order_ref}",
            'state': state,
            'date_order': purchase_date,
            'partner_id': contact_partner.id,
            'pricelist_id': self._find_or_create_pricelist(currency).id,
            'order_line': [(0, 0, order_line_values) for order_line_values in order_lines_values],
            'invoice_status': 'no',
            'partner_shipping_id': delivery_partner.id,
            'require_signature': False,
            'require_payment': False,
            'fiscal_position_id': fiscal_position.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id.id,
            'team_id': self.team_id.id,
            'amazon_order_ref': amazon_order_ref,
            'amazon_channel': 'fba' if fulfillment_channel == 'AFN' else 'fbm',
        }
        if self.location_id.warehouse_id:
            order_vals['warehouse_id'] = self.location_id.warehouse_id.id
        # ----------- OVERRIDE -----------
        order_env = self.env['sale.order']
        if self.is_keeping_order_draft:
            order_vals['state'] = 'draft'
        if self.use_amz_ref_so_number:
            order_vals['name'] = amazon_order_ref
        order_vals.update(order_env.update_amazon_information(
            order_data, amz_account=self
        ))
        # ----------- END OVERRIDE -----------
        return order_env.with_context(
            mail_create_nosubscribe=True
        ).with_company(self.company_id).create(order_vals)

    @api.model
    def cron_sync_amazon_fbm_stock(self):
        accounts = self.env['amazon.account'].search([])
        accounts.marketplaces_sync_fbm_stock()

    def marketplaces_sync_fbm_stock(self, amz_products=False, marketplaces=False):
        location_dict = {}
        # quant_env = self.env['stock.quant']
        stock_loc = self.env.ref('stock.stock_location_stock')
        # amazon_utils.refresh_aws_credentials(self)
        for account in self:
            if not marketplaces:
                marketplaces = account.active_marketplace_ids
            for mp in marketplaces:
                fbm_location = (mp.fbm_location_id
                    if mp.fbm_location_id else stock_loc
                )
                if fbm_location not in location_dict:
                    location_dict[fbm_location] = self.env['amazon.marketplace']
                location_dict[fbm_location] |= mp
            _logger.info(str(location_dict))
            for location, mps in location_dict.items():
                if not amz_products:
                    # avail_quants = quant_env.search(
                    #     [('location_id', 'child_of', location.id)]
                    # )
                    amz_products = mps.mapped('amazon_offer_ids').filtered(
                        lambda p: p.is_mfn
                    )
                    # instock_products = avail_quants.mapped('product_id')
                    amz_products = amz_products.mapped('product_id')  # & instock_products
                    # amz_products = mps.mapped('amazon_offer_ids').filtered(
                    #     lambda p: p.product_id in instock_products
                    # )

                step = FEED_BULK_RECORD_LIMIT_RATE
                for i in range(0, len(amz_products), step):
                    amz_products[i:i+step].export_stock_quantity(account, location, mps)

    def action_open_sp_api_status(self):
        return {
            "type": "ir.actions.act_url",
            "url": "https://sellercentral.amazon.com/sp-api-status",
            "target": "new",
        }

    def _prepare_order_lines_values(self, order_data, currency, fiscal_pos, shipping_product):
        """ Prepare the values for the order lines to create based on Amazon data.

        Note: self.ensure_one()

        :param dict order_data: The order data related to the item data.
        :param record currency: The currency of the sales order, as a `res.currency` record.
        :param record fiscal_pos: The fiscal position of the sales order, as an
                                  `account.fiscal.position` record.
        :param record shipping_product: The shipping product matching the shipping code, as a
                                        `product.product` record.
        :return: The order lines values.
        :rtype: dict
        """
        def pull_items_data(amazon_order_ref_):
            """ Pull all item data for the order to synchronize.

            :param str amazon_order_ref_: The Amazon reference of the order to synchronize.
            :return: The items data.
            :rtype: list
            """
            items_data_ = []
            # Order items are pulled in batches. If more order items than those returned can be
            # synchronized, the request results are paginated and the next page holds another batch.
            has_next_page_ = True
            while has_next_page_:
                # Pull the next batch of order items.
                items_batch_data_, has_next_page_ = amazon_utils.pull_batch_data(
                    self, 'getOrderItems', {}, path_parameter=amazon_order_ref_
                )
                items_data_ += items_batch_data_['OrderItems']
            return items_data_

        def convert_to_order_line_values(**kwargs_):
            """ Convert and complete a dict of values to comply with fields of `sale.order.line`.

            :param dict kwargs_: The values to convert and complete.
            :return: The completed values.
            :rtype: dict
            """
            subtotal_ = kwargs_.get('subtotal', 0)
            quantity_ = kwargs_.get('quantity', 1)
            return {
                'name': kwargs_.get('description', ''),
                'product_id': kwargs_.get('product_id'),
                'price_unit': subtotal_ / quantity_ if quantity_ else 0,
                'tax_id': [(6, 0, kwargs_.get('tax_ids', []))],
                'product_uom_qty': quantity_,
                'discount': (kwargs_.get('discount', 0) / subtotal_) * 100 if subtotal_ else 0,
                'display_type': kwargs_.get('display_type', False),
                'amazon_item_ref': kwargs_.get('amazon_item_ref'),
                'amazon_offer_id': kwargs_.get('amazon_offer_id'),
            }

        self.ensure_one()

        amazon_order_ref = order_data['AmazonOrderId']
        marketplace_api_ref = order_data['MarketplaceId']

        items_data = pull_items_data(amazon_order_ref)

        order_lines_values = []
        for item_data in items_data:
            # Prepare the values for the product line.
            sku = item_data['SellerSKU']
            marketplace = self.active_marketplace_ids.filtered(
                lambda m: m.api_ref == marketplace_api_ref
            )
            offer = self._find_or_create_offer(sku, marketplace)
            product_taxes = offer.product_id.taxes_id.filtered(
                lambda t: t.company_id.id == self.company_id.id
            )
            main_condition = item_data.get('ConditionId')
            sub_condition = item_data.get('ConditionSubtypeId')
            if not main_condition or main_condition.lower() == 'new':
                description = "[%s] %s" % (sku, item_data['Title'])
            else:
                item_title = item_data['Title']
                description = _(
                    "[%s] %s\nCondition: %s - %s", sku, item_title, main_condition, sub_condition
                )
            sales_price = float(item_data.get('ItemPrice', {}).get('Amount', 0.0))
            tax_amount = float(item_data.get('ItemTax', {}).get('Amount', 0.0))
            original_subtotal = sales_price - tax_amount \
                if marketplace.tax_included else sales_price
            taxes = fiscal_pos.map_tax(product_taxes) if fiscal_pos else product_taxes
            subtotal = self._recompute_subtotal(
                original_subtotal, tax_amount, taxes, currency, fiscal_pos
            )
            promo_discount = float(item_data.get('PromotionDiscount', {}).get('Amount', '0'))
            promo_disc_tax = float(item_data.get('PromotionDiscountTax', {}).get('Amount', '0'))
            original_promo_discount_subtotal = promo_discount - promo_disc_tax \
                if marketplace.tax_included else promo_discount
            promo_discount_subtotal = self._recompute_subtotal(
                original_promo_discount_subtotal, promo_disc_tax, taxes, currency, fiscal_pos
            )
            amazon_item_ref = item_data['OrderItemId']
            order_lines_values.append(convert_to_order_line_values(
                product_id=offer.product_id.id,
                description=description,
                subtotal=subtotal,
                tax_ids=taxes.ids,
                quantity=item_data['QuantityOrdered'],
                discount=promo_discount_subtotal,
                amazon_item_ref=amazon_item_ref,
                amazon_offer_id=offer.id,
            ))

            # Prepare the values for the gift wrap line.
            if item_data.get('IsGift', 'false') == 'true':
                item_gift_info = item_data.get('BuyerInfo', {})
                gift_wrap_code = item_gift_info.get('GiftWrapLevel')
                gift_wrap_price = float(item_gift_info.get('GiftWrapPrice', {}).get('Amount', '0'))
                if gift_wrap_code and gift_wrap_price != 0:
                    gift_wrap_product = self._find_matching_product(
                        gift_wrap_code, 'default_product', 'Amazon Sales', 'consu'
                    )
                    gift_wrap_product_taxes = gift_wrap_product.taxes_id.filtered(
                        lambda t: t.company_id.id == self.company_id.id
                    )
                    gift_wrap_taxes = fiscal_pos.map_tax(gift_wrap_product_taxes) \
                        if fiscal_pos else gift_wrap_product_taxes
                    gift_wrap_tax_amount = float(
                        item_gift_info.get('GiftWrapTax', {}).get('Amount', '0')
                    )
                    original_gift_wrap_subtotal = gift_wrap_price - gift_wrap_tax_amount \
                        if marketplace.tax_included else gift_wrap_price
                    gift_wrap_subtotal = self._recompute_subtotal(
                        original_gift_wrap_subtotal,
                        gift_wrap_tax_amount,
                        gift_wrap_taxes,
                        currency,
                        fiscal_pos,
                    )
                    order_lines_values.append(convert_to_order_line_values(
                        product_id=gift_wrap_product.id,
                        description=_(
                            "[%s] Gift Wrapping Charges for %s",
                            gift_wrap_code, offer.product_id.name
                        ),
                        subtotal=gift_wrap_subtotal,
                        tax_ids=gift_wrap_taxes.ids,
                        amazon_item_ref="%s-%s" % (amazon_item_ref, 'gift_wrap'),
                    ))
                gift_message = item_gift_info.get('GiftMessageText')
                if gift_message:
                    order_lines_values.append(convert_to_order_line_values(
                        description=_("Gift message:\n%s", gift_message),
                        display_type='line_note',
                        amazon_item_ref="%s-%s" % (amazon_item_ref, 'gift_wrap'),
                    ))

            # Prepare the values for the delivery charges.
            shipping_code = order_data.get('ShipServiceLevel')
            if shipping_code:
                shipping_price = float(item_data.get('ShippingPrice', {}).get('Amount', '0'))
                shipping_product_taxes = shipping_product.taxes_id.filtered(
                    lambda t: t.company_id.id == self.company_id.id
                )
                shipping_taxes = fiscal_pos.map_tax(shipping_product_taxes) if fiscal_pos \
                    else shipping_product_taxes
                shipping_tax_amount = float(item_data.get('ShippingTax', {}).get('Amount', '0'))
                origin_ship_subtotal = shipping_price - shipping_tax_amount \
                    if marketplace.tax_included else shipping_price
                shipping_subtotal = self._recompute_subtotal(
                    origin_ship_subtotal, shipping_tax_amount, shipping_taxes, currency, fiscal_pos
                )
                ship_discount = float(item_data.get('ShippingDiscount', {}).get('Amount', '0'))
                ship_disc_tax = float(item_data.get('ShippingDiscountTax', {}).get('Amount', '0'))
                origin_ship_disc_subtotal = ship_discount - ship_disc_tax \
                    if marketplace.tax_included else ship_discount
                ship_discount_subtotal = self._recompute_subtotal(
                    origin_ship_disc_subtotal, ship_disc_tax, shipping_taxes, currency, fiscal_pos
                )
                order_lines_values.append(convert_to_order_line_values(
                    product_id=shipping_product.id,
                    description=_(
                        "[%s] Delivery Charges for %s", shipping_code, offer.product_id.name
                    ),
                    subtotal=shipping_subtotal,
                    tax_ids=shipping_taxes.ids,
                    discount=ship_discount_subtotal,
                    amazon_item_ref="%s-%s" % (amazon_item_ref, 'shipping'),
                ))

        return order_lines_values
