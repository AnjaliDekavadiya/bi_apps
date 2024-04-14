# See LICENSE file for full copyright and licensing details.

import logging

from odoo import models


_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _magento2_cancel_order(self, *args, **kw):
        _logger.info('SaleOrder _magento2_cancel_order(). Not implemented.')
        pass

    def _magento2_shipped_order(self, *args, **kw):
        _logger.info('SaleOrder _magento2_shipped_order(). Not implemented.')
        pass

    def _magento2_paid_order(self, *args, **kw):
        _logger.info('SaleOrder _magento2_paid_order()')
        status = self.env['sale.order.sub.status']\
            .from_external(self.integration_id, 'processing')  # TODO: attention, hardcode!
        self.sub_status_id = status.id
