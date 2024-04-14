
import logging
import psycopg2
import time
from urllib.parse import quote_plus

from odoo import api, fields, models

from odoo.addons.sale_amazon import const, utils as amazon_utils
from odoo.exceptions import UserError
from odoo.service.model import PG_CONCURRENCY_ERRORS_TO_RETRY as CONCURRENCY_ERRORS

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    amz_fulfillment_order_help = """
        RECEIVED:The fulfillment order was received by Amazon Marketplace Web Service (Amazon MWS)
                 and validated. Validation includes determining that the destination address is
                 valid and that Amazon's records indicate that the seller has enough sellable
                 (undamaged) inventory to fulfill the order. The seller can cancel a fulfillment
                 order that has a status of RECEIVED
        INVALID:The fulfillment order was received by Amazon Marketplace Web Service (Amazon MWS)
                but could not be validated. The reasons for this include an invalid destination
                address or Amazon's records indicating that the seller does not have enough sellable
                inventory to fulfill the order. When this happens, the fulfillment order is invalid
                and no items in the order will ship
        PLANNING:The fulfillment order has been sent to the Amazon Fulfillment Network to begin
                 shipment planning, but no unit in any shipment has been picked from inventory yet.
                 The seller can cancel a fulfillment order that has a status of PLANNING
        PROCESSING:The process of picking units from inventory has begun on at least one shipment
                   in the fulfillment order. The seller cannot cancel a fulfillment order that
                   has a status of PROCESSING
        CANCELLED:The fulfillment order has been cancelled by the seller.
        COMPLETE:All item quantities in the fulfillment order have been fulfilled.
        COMPLETE_PARTIALLED:Some item quantities in the fulfillment order were fulfilled; the rest
                            were either cancelled or unfulfillable.
        UNFULFILLABLE: item quantities in the fulfillment order could be fulfilled because the
                Amazon fulfillment center workers found no inventory
        for those items or found no inventory that was in sellable (undamaged) condition.
    """

    stock_move_ids = fields.One2many(
        comodel_name="stock.move",
        inverse_name="sale_id",
        string="Stock Moves",
        readonly=True
    )
    is_amz_business_order = fields.Boolean()
    is_invoice_uploaded_amz = fields.Boolean(
        string="All Invoices Uploaded to Amazon",
        compute="_compute_is_invoice_uploaded_amz",
        store=True,
    )
    amz_fulfillment_action = fields.Selection([
        ('Ship', 'Ship'), ('Hold', 'Hold')],
        string="Fulfillment Action", default="Hold"
    )
    amz_displayable_order_date = fields.Date(
        "Displayable Order Date", help="Display Date in package")
    amz_shipment_service_level_category = fields.Selection([
            ('Standard', 'Standard'),
            ('Expedited', 'Expedited'),
            ('Priority', 'Priority'),
            ('ScheduledDelivery', 'ScheduledDelivery')
        ], string="Shipment Category", default='Standard',
        help="ScheduledDelivery used only for Japan")
    amz_fulfillment_policy = fields.Selection([
            ('FillOrKill', 'FillOrKill'),
            ('FillAll', 'FillAll'),
            ('FillAllAvailable', 'FillAllAvailable')
        ], string="Fulfillment Policy", default="FillOrKill"
    )
    is_amz_outbound_order = fields.Boolean("Amazon Outbound Order?")
    amz_delivery_start_time = fields.Datetime(
        "Delivery Start Time", help="Delivery Estimated Start Time"
    )
    amz_delivery_end_time = fields.Datetime(
        "Delivery End Time", help="Delivery Estimated End Time"
    )
    is_amz_outbound_exported = fields.Boolean("Outbound exported In Amazon?")
    notify_by_email = fields.Boolean(
        "Notify By Email", help="If true then system will notify by email to followers"
    )
    amz_fulfillment_order_status = fields.Selection([
            ('RECEIVED', 'RECEIVED'),
            ('PLANNING', 'PLANNING'),
            ('PROCESSING', 'PROCESSING'),
            ('CANCELLED', 'CANCELLED'),
            ('COMPLETE', 'COMPLETE'),
            ('COMPLETE_PARTIALLED', 'COMPLETE_PARTIALLED'),
            ('UNFULFILLABLE', 'UNFULFILLABLE'),
            ('INVALID', 'INVALID'),
        ], string="Fulfillment Order Status", help=amz_fulfillment_order_help)


    @api.depends("invoice_ids", "invoice_ids.is_pushed_to_amz")
    def _compute_is_invoice_uploaded_amz(self):
        for order in self:
            order.is_invoice_uploaded_amz = all(
                order.invoice_ids.mapped("is_pushed_to_amz")
            )

    @api.model
    def bulk_import_amazon_orders(self, account, amazon_order_refs):
        # Breakdown the list of order references into batches of 50.
        chunk_size = 40
        for i in range(0, len(amazon_order_refs), chunk_size):
            chunk = amazon_order_refs[i:i+chunk_size]
            self.import_amazon_order(account, chunk)
            time.sleep(10)

    @api.model
    def import_amazon_order(self, account, amazon_order_refs):
        orders = self.env['sale.order']
        sync_log_env = self.env['amazon.synchronization.log']
        payload = {
             "AmazonOrderIds": ",".join(amazon_order_refs) if isinstance(amazon_order_refs, list) else amazon_order_refs,
        }
        orders_batch_data, has_next_page =  amazon_utils.pull_batch_data(
            account, 'getOrders', payload
        )
        orders_data = orders_batch_data['Orders']

        # Process the batch one order data at a time.
        for order_data in orders_data:
            try:
                with self.env.cr.savepoint():
                    orders |= account._process_order_data(order_data)
            except amazon_utils.AmazonRateLimitError as error:
                # raise  # Don't treat a rate limit error as a business error.
                _logger.info(
                    "Rate limit reached while synchronizing sales orders for Amazon account with "
                    "id %s. Operation: %s", account.id, error.operation
                )
                continue
            except Exception as error:
                amazon_order_ref = order_data['AmazonOrderId']
                if isinstance(error, psycopg2.OperationalError) \
                    and error.pgcode in CONCURRENCY_ERRORS:
                    _logger.info(
                        "A concurrency error occurred while processing the order data "
                        "with amazon_order_ref %s for Amazon account with id %s. "
                        "Discarding the error to trigger the retry mechanism.",
                        amazon_order_ref, account.id
                    )
                    # Let the error bubble up so that either the request can be retried
                    # up to 5 times or the cron job rollbacks the cursor and reschedules
                    # itself later, depending on which of the two called this method.
                    raise
                else:
                    _logger.exception(
                        "A business error occurred while processing the order data "
                        "with amazon_order_ref %s for Amazon account with id %s. "
                        "Skipping the order data and moving to the next order.",
                        amazon_order_ref, account.id
                    )
                    # Dismiss business errors to allow the synchronization to skip the
                    # problematic orders and require synchronizing them manually.
                    self.env.cr.rollback()
                    sync_log_env.order_sync_failure(account, order_data, error_msg=error)
                    continue  # Skip these order data and resume with the next ones.

            with amazon_utils.preserve_credentials(account):
                self.env.cr.commit()  # Commit to mitigate an eventual cron kill.
        return orders

    def create_outbound_shipment(self):
        fba_wh_orders = self.filtered(lambda order: order.warehouse_id.is_fba_wh)
        if not fba_wh_orders:
            return False
        amazon_outbound_order_wizard_env = self.env['amazon.outbound.order.wizard']
        wizard_id = amazon_outbound_order_wizard_env.create({
            'account_id': self.env["amazon.account"].search([]).id,
            'sale_order_ids': [(6, 0, fba_wh_orders.ids)],
        })
        return amazon_outbound_order_wizard_env.wizard_view(wizard_id)

    def cancel_amz_outbound_order(self):
        amazon_utils.refresh_aws_credentials(self.amz_account_id)
        amazon_utils.ensure_account_is_set_up(self.amz_account_id)
        amazon_utils.make_sp_api_request(
            self.amz_account_id,
            operation='cancelFulfillmentOrder',
            path_parameter=quote_plus(self.amazon_order_ref),
            method='PUT'
        )
        self.write({'amz_fulfillment_order_status': "CANCELLED"})

    def generate_amz_outbound_order_data(self):
        order_data = {}
        order_data.update({
            'sellerFulfillmentOrderId': self.name,
            'displayableOrderId': self.amazon_order_ref,
            'displayableOrderDate': fields.Date.to_string(self.amz_displayable_order_date),
            'displayableOrderComment': self.amazon_order_ref,  # str(self.note) or '',
            'shippingSpeedCategory': self.amz_shipment_service_level_category,
            'fulfillmentAction': self.amz_fulfillment_action,
            'fulfillmentPolicy': self.amz_fulfillment_policy,
            'shipFromCountryCode': self.warehouse_id.partner_id.country_id.code,
            'destinationAddress': {},
            'items': [],
        })
        if self.amz_delivery_start_time and self.amz_delivery_end_time:
            start_date = time.strptime(self.amz_delivery_start_time, "%Y-%m-%d %H:%M:%S")
            start_date = time.strftime("%Y-%m-%dT%H:%M:%S", start_date)
            start_date = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(
                time.mktime(time.strptime(start_date, "%Y-%m-%dT%H:%M:%S"))))
            start_date = str(start_date) + 'Z'

            end_date = time.strptime(self.amz_delivery_end_time, "%Y-%m-%d %H:%M:%S")
            end_date = time.strftime("%Y-%m-%dT%H:%M:%S", end_date)
            end_date = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(
                time.mktime(time.strptime(end_date, "%Y-%m-%dT%H:%M:%S"))))
            end_date = str(start_date) + 'Z'

            order_data.update({
                'deliveryWindow.startDate': start_date,
                'deliveryWindow.endDate': end_date,
            })

        order_data["destinationAddress"].update({
            'name': self.partner_shipping_id.name,
            'addressLine1': ' '.join([self.partner_shipping_id.street or '',
                                      self.partner_shipping_id.street_no or '']),
            'addressLine2': self.partner_shipping_id.street2 or '',
            'addressLine3': "",
            'city': self.partner_shipping_id.city or '',
            'stateOrRegion': str(self.partner_shipping_id.state_id and
                                 self.partner_shipping_id.state_id.code or ''),
            'postalCode': self.partner_shipping_id.zip or '',
            'countryCode': self.partner_shipping_id.country_id.code or '',
        })

        for line in self.order_line:
            if not line.product_id or line.product_id.detailed_type == 'service':
                continue
            line_vals = {
                "sellerSku": line.amazon_product_id.sku,
                "sellerFulfillmentOrderItemId": line.amazon_product_id.sku,
                "quantity": int(line.product_uom_qty),
            }
            order_data["items"].append(line_vals)

        return order_data

    @api.model
    def cron_upload_invoice_amazon(self):
        orders = self.search([
            ('amazon_order_ref', '!=', False),
            ('is_invoice_uploaded_amz', '=', False),
            ('is_amz_outbound_order', '=', False),
            # ('amazon_channel', '=', "fba"),
        ], limit=50)
        invoices = self.env['account.move']
        for order in orders:
            if not order.order_line.mapped("amz_shipment_id"):
                continue
            invoices |= order.invoice_ids.filtered(
                lambda inv: inv.state == 'posted' and not inv.is_pushed_to_amz)
        invoices.amazon_upload_pdf_invoice()

    def button_batch_create_invoices(self):
        inv_env = self.env['sale.advance.payment.inv']
        for sale in self:
            if sale.delivery_status != 'full' or sale.invoice_status != 'to invoice':
                continue
            inv_wiz = inv_env.with_context(active_ids=sale.ids).create({})
            inv_wiz.create_invoices()

        self.mapped('invoice_ids').filtered(
            lambda inv: inv.state == "draft").action_post()
