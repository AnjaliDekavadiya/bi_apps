import json
import logging
import time

import dateutil.parser
import psycopg2

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.service.model import PG_CONCURRENCY_ERRORS_TO_RETRY as CONCURRENCY_ERRORS

from odoo.addons.sale_amazon import const, utils as amazon_utils


_logger = logging.getLogger(__name__)



class AmazonOperationWizard(models.TransientModel):
    _name = "amazon.operation.wizard"

    amz_account_id = fields.Many2one(
        'amazon.account',
        string="Amazon Accounts",
        default=lambda self: self.env['amazon.account'].search([], limit=1)
    )
    marketplace_ids = fields.Many2many(
        'amazon.marketplace',
        string="Marketplaces",
        domain="[('id', 'in', active_marketplace_ids)]",
    )
    active_marketplace_ids = fields.Many2many(
        string="Account's Active Marketplaces",
        comodel_name='amazon.marketplace',
        related="amz_account_id.active_marketplace_ids",
    )
    is_import_order = fields.Boolean("Import Orders")
    orders_date_from = fields.Datetime(string="From")
    orders_date_to = fields.Datetime(string="To", help="Please set the end time 5 prior actual time.")
    is_export_shipment = fields.Boolean("Export Shipments")
    is_export_fbm_stock = fields.Boolean("Export FBM Stock")
    last_orders_sync = fields.Datetime()


    @api.onchange('amz_account_id')
    def onchange_account_id(self):
        for wiz in self:
            if wiz.amz_account_id:
                wiz.marketplace_ids = wiz.amz_account_id.active_marketplace_ids
            else:
                wiz.marketplace_ids = []

    @api.onchange('orders_date_from')
    def onchange_orders_date_from(self):
        for wiz in self:
            if wiz.orders_date_from:
                wiz.last_orders_sync = wiz.orders_date_from

    def execute_amazon_operations(self):
        if self.is_import_order:
            return self.import_amazon_orders(
                self.amz_account_id,
                self.orders_date_from,
                self.orders_date_to,
                self.marketplace_ids
            )
        if self.is_export_shipment:
            return self.export_amazon_shipments([self.amz_account_id.id])
        if self.is_export_fbm_stock:
            return self.export_fbm_stock(self.amz_account_id, self.marketplace_ids)

    def import_amazon_orders(self, account, from_date, to_date,
                             marketplace_ids=False, auto_commit=True,):
        """ Synchronize the sales orders that were recently updated on Amazon.

        If called on an empty recordset, the orders of all active accounts are synchronized instead.

        Note: This method is called by the `ir_cron_sync_amazon_orders` cron.

        :param bool auto_commit: Whether the database cursor should be committed as soon as an order
                                 is successfully synchronized.
        :return: None
        """
        orders = self.env['sale.order']
        sync_log_env = self.env['amazon.synchronization.log']
        amazon_utils.refresh_aws_credentials(account)  # Prevent redundant refresh requests.

        account = account[0]  # Avoid pre-fetching after each cache invalidation.
        amazon_utils.ensure_account_is_set_up(account)

        created_after = from_date if from_date else self.last_orders_sync
        created_before = to_date if to_date else fields.Datetime.now()

        # Pull all recently updated orders and save the progress during synchronization.
        payload = {
            'CreatedAfter': created_after.isoformat(sep='T'),
            'CreatedBefore': created_before.isoformat(sep='T'),
            'MarketplaceIds': ','.join(marketplace_ids.mapped('api_ref')),
        }
        try:
            # Orders are pulled in batches of up to 100 orders. If more can be synchronized, the
            # request results are paginated and the next page holds another batch.
            has_next_page = True
            while has_next_page:
                # Pull the next batch of orders data.
                orders_batch_data, has_next_page = amazon_utils.pull_batch_data(
                    account, 'getOrders', payload
                )
                orders_data = orders_batch_data['Orders']
                status_update_upper_limit = dateutil.parser.parse(
                    orders_batch_data['CreatedBefore']
                )

                # Process the batch one order data at a time.
                for order_data in orders_data:
                    try:
                        with self.env.cr.savepoint():
                            orders |= account._process_order_data(order_data)
                    except amazon_utils.AmazonRateLimitError:
                        raise  # Don't treat a rate limit error as a business error.
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

                    # The synchronization of this order went through, use its last status update
                    # as a backup and set it to be the last synchronization date of the account.
                    last_order_update = dateutil.parser.parse(order_data['PurchaseDate'])
                    self.last_orders_sync = last_order_update.replace(tzinfo=None)
                    if auto_commit:
                        with amazon_utils.preserve_credentials(account):
                            self.env.cr.commit()  # Commit to mitigate an eventual cron kill.
        except amazon_utils.AmazonRateLimitError as error:
            _logger.info(
                "Rate limit reached while synchronizing sales orders for Amazon account with "
                "id %s. Operation: %s", account.id, error.operation
            )
            time.sleep(60)  # Wait for 1 minute before retrying.
            # continue  # The remaining orders will be pulled later when the cron runs again.

        # There are no more orders to pull and the synchronization went through. Set the API
        # upper limit on order status update to be the last synchronization date of the account.
        self.last_orders_sync = status_update_upper_limit.replace(tzinfo=None)

        return {
            'name': _('Imported Amazon Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('id', 'in', orders.ids)],
        }

    @api.model
    def export_amazon_shipments(self, account_ids=()):
        """ Synchronize the deliveries that were marked as done with Amazon.

        We assume that the combined set of pickings (of all accounts) to be synchronized will always
        be too small for the cron to be killed before it finishes synchronizing all pickings.

        If provided, the tuple of account ids restricts the pickings waiting for synchronization to
        those whose account is listed. If it is not provided, all pickings are synchronized.

        Note: This method is called by the `ir_cron_sync_amazon_pickings` cron.

        :param tuple account_ids: The accounts whose deliveries should be synchronized, as a tuple
                                  of `amazon.account` record ids.
        :return: None
        """
        pickings_by_account = {}

        for picking in self.env['stock.picking'].search([('amazon_sync_pending', '=', True)]):
            if picking.sale_id.order_line:
                offer = picking.sale_id.order_line[0].amazon_offer_id
                account = offer and offer.account_id  # The offer could have been deleted.
                if not account or (account_ids and account.id not in account_ids):
                    continue
                pickings_by_account.setdefault(account, self.env['stock.picking'])
                pickings_by_account[account] += picking

        # Prevent redundant refresh requests.
        accounts = self.env['amazon.account'].browse(account.id for account in pickings_by_account)
        amazon_utils.refresh_aws_credentials(accounts)

        for account, pickings in pickings_by_account.items():
            pickings._confirm_shipment(account)

    @api.model
    def export_fbm_stock(self, accounts, marketplaces):
        amazon_utils.refresh_aws_credentials(accounts)
        accounts.marketplaces_sync_fbm_stock(marketplaces=marketplaces)
