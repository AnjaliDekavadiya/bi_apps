# See LICENSE file for full copyright and licensing details.

from odoo import models
from ..woocommerce_api_client import \
    ORDER_STATUS_PROCESSING, ORDER_STATUS_COMPLETED, ORDER_STATUS_CANCELLED

import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _woocommerce_cancel_order(self, *args, **kw):
        _logger.info('SaleOrder _woocommerce_cancel_order()')
        status = self.env['sale.order.sub.status'].from_external(
            self.integration_id, ORDER_STATUS_CANCELLED)
        self.sub_status_id = status.id

    def _woocommerce_shipped_order(self, *args, **kw):
        _logger.info('SaleOrder _woocommerce_shipped_order()')
        status = self.env['sale.order.sub.status'].from_external(
            self.integration_id, ORDER_STATUS_COMPLETED)
        self.sub_status_id = status.id

    def _woocommerce_paid_order(self, *args, **kw):
        _logger.info('SaleOrder _woocommerce_paid_order()')
        status = self.env['sale.order.sub.status'].from_external(
            self.integration_id, ORDER_STATUS_PROCESSING)
        self.sub_status_id = status.id
