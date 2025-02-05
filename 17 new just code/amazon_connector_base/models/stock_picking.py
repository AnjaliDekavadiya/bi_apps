import logging
from datetime import datetime
from xml.etree import ElementTree

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.sale_amazon import const
from odoo.addons.sale_amazon import utils as amazon_utils


_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'


    def _confirm_shipment(self, account):
        """ Send a confirmation request for each of the current deliveries to Amazon.

        :param record account: The Amazon account of the delivery to confirm on Amazon, as an
                               `amazon.account` record.
        :return: None
        """
        def build_feed_messages(root_):
            """ Build the 'Message' elements to add to the feed.

            :param Element root_: The root XML element to which messages should be added.
            :return: None
            """
            for picking_ in self:
                # Build the message base.
                message_ = ElementTree.SubElement(root_, 'Message')
                order_fulfillment_ = ElementTree.SubElement(message_, 'OrderFulfillment')
                amazon_order_ref_ = picking_.sale_id.amazon_order_ref
                ElementTree.SubElement(order_fulfillment_, 'AmazonOrderID').text = amazon_order_ref_
                shipping_date_ = datetime.now().isoformat()
                ElementTree.SubElement(order_fulfillment_, 'FulfillmentDate').text = shipping_date_

                # Add the fulfillment data.
                fulfillment_data_ = ElementTree.SubElement(
                    order_fulfillment_, 'FulfillmentData'
                )
                ElementTree.SubElement(
                    fulfillment_data_, 'CarrierName'
                ).text = picking_._get_formatted_carrier_name()
                ElementTree.SubElement(
                    fulfillment_data_, 'ShipperTrackingNumber'
                ).text = picking_.carrier_tracking_ref

                # Add the items.
                confirmed_order_lines_ = picking_._get_confirmed_order_lines()
                items_data_ = confirmed_order_lines_.mapped(
                    lambda l_: (l_.amazon_item_ref, l_.product_uom_qty)
                )  # Take the quantity from the sales order line in case the picking contains a BoM.
                for amazon_item_ref_, item_quantity_ in items_data_:
                    item_ = ElementTree.SubElement(order_fulfillment_, 'Item')
                    ElementTree.SubElement(item_, 'AmazonOrderItemCode').text = amazon_item_ref_
                    ElementTree.SubElement(item_, 'Quantity').text = str(int(item_quantity_))

                # Add the shipping location.
                location_ = account.location_id.warehouse_id.partner_id
                ship_from_ = ElementTree.SubElement(order_fulfillment_, 'ShipFromAddress')
                ElementTree.SubElement(ship_from_, 'Name').text = location_.name[:30]
                ElementTree.SubElement(ship_from_, 'AddressFieldOne').text = location_.street[:180]
                ElementTree.SubElement(ship_from_, 'CountryCode').text = location_.country_id.code

        # amazon_utils.ensure_account_is_set_up(account)
        feed_env = self.env['feed.submission.log']

        xml_feed = amazon_utils.build_feed(account, 'OrderFulfillment', build_feed_messages)
        feed_vals = {
            'account_id': account.id,
            'feed_message': xml_feed,
            'feed_type': 'POST_ORDER_FULFILLMENT_DATA',
        }
        feed_vals['amz_marketplace_ids'] = [(6, 0, self.mapped(
            "sale_id.amz_marketplace_id").ids)]

        feed_env.create(feed_vals)
        self.write({'amazon_sync_pending': False})

