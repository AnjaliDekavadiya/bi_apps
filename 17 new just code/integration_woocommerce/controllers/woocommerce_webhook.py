#  See LICENSE file for full copyright and licensing details.

import logging

from odoo.http import Controller, route, request
from odoo.tools.config import config
from odoo.addons.integration.controllers.integration_webhook import IntegrationWebhook
from odoo.addons.integration.controllers.utils import build_environment, validate_integration

from ..woocommerce_api_client import WOOCOMMERCE, ORDER_STATUS_CANCELLED


_logger = logging.getLogger(__name__)

woocommerce_webhook_setup_mode = config.get('woocommerce_webhook_setup_mode')


class WoocommerceWebhook(Controller, IntegrationWebhook):

    """
    headers = {
        Host: 0256-2a01-110f-44a2-1a00-992f-e54b-beb8-51d0.eu.ngrok.io
        User-Agent: WooCommerce/7.2.1 Hookshot (WordPress/6.1.1)
        Content-Length: 4927
        Accept-Encoding: deflate;q=1.0, compress;q=0.5, gzip;q=0.5
        Content-Type: application/json
        X-Forwarded-For: 141.95.36.78
        X-Forwarded-Proto: https
        X-Wc-Webhook-Delivery-Id: fbef05aa13727f9f21b1b5ffd4abcc4c
        X-Wc-Webhook-Event: updated
        X-Wc-Webhook-Id: 1
        X-Wc-Webhook-Resource: order
        X-Wc-Webhook-Signature: al0t6j/VPqP3GxpUs3mPHvqc/f8qc/yzG7vMghBKlS0=
        X-Wc-Webhook-Source: https://woocommerce.ventor.tech/
        X-Wc-Webhook-Topic: order.updated
    }
    """

    SHOP_NAME = 'X-Wc-Webhook-Source'
    TOPIC_NAME = 'X-Wc-Webhook-Topic'
    NEW_ORDER_METHOD_NAME = 'order_created'

    if woocommerce_webhook_setup_mode:
        _kwargs = {
            'type': 'http',
            'auth': 'none',
            'methods': ['POST'],
            'csrf': False,
        }
    else:
        _kwargs = {
            'type': 'json',
            'auth': 'none',
            'methods': ['POST'],
            'csrf': False,
        }

    @property
    def integration_type(self):
        return WOOCOMMERCE

    @route(f'/<string:dbname>/integration/{WOOCOMMERCE}/<int:integration_id>/orders', **_kwargs)
    def woocommerce_receive_webhook(self, *args, **kw):
        """
        Confirmation of webhook in WooCommerce
        """
        _logger.info('Call woocommerce webhook controller: woocommerce_confirm_webhook()')
        headers = self._get_headers()
        if headers['Content-Type'] == 'application/json':
            return self.woocommerce_receive_orders(*args, **kw)

        # This 'return' need for successful setup woocommerce webhook
        return 'OK'

    @build_environment
    @validate_integration
    def woocommerce_receive_orders(self, *args, **kw):
        """
        Expected methods:
            order.updated (Order Updated)
            order.created (Order Created)
        """
        _logger.info('Call woocommerce webhook controller: woocommerce_receive_orders()')
        integration = request.env['sale.integration'].browse(kw['integration_id'])
        return self._receive_order_generic(integration)

    def order_created(self, integration, external_order_id):
        """Order Created"""
        _logger.info('Call woocommerce webhook controller: order_created()')
        return integration.integration_receive_orders_cron(cron_operation=False)  # TODO: by ID

    def order_updated(self, input_file):
        """Order Status Updated"""
        _logger.info('Call woocommerce webhook controller actionOrderHistoryAddAfter()')

        status_code = self._get_value_from_post_data('status')
        sub_status_id, external_sub_status = self._get_order_sub_status_tuple(
            input_file.si_id,
            status_code,
        )
        if not sub_status_id:
            _logger.info('Woocommerce webhook: external sub-status not recognized.')
            return False

        data = self._prepare_pipeline_data()

        if external_sub_status.code == ORDER_STATUS_CANCELLED:
            return input_file._run_cancel_order(data)

        return input_file._build_and_run_order_pipeline(data)

    def _prepare_pipeline_data(self):
        post_data = self._get_post_data()
        vals = {
            'payment_method': post_data['payment_method'],
            'integration_workflow_states': [post_data['status']],
        }
        return vals

    def _check_webhook_digital_sign(self, integration):
        return True  # TODO

    def _get_hook_name_method(self):
        headers = self._get_headers()
        topic = headers[self.TOPIC_NAME]
        return '_'.join(topic.split('.'))

    def _get_essential_headers(self):
        return [
            self.SHOP_NAME,
            self.TOPIC_NAME,
            'X-Wc-Webhook-Signature',
        ]
