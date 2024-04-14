#  See LICENSE file for full copyright and licensing details.

import logging

from odoo.http import Controller, route, request
from odoo.addons.integration.controllers.utils import build_environment, validate_integration
from odoo.addons.integration.controllers.integration_webhook import IntegrationWebhook
from odoo.addons.integration.controllers.external_integration import INTEGRATION_API_HEADER

from ..magento2_api_client import MAGENTO_TWO


_logger = logging.getLogger(__name__)


class Magento2Webhook(Controller, IntegrationWebhook):

    _kwargs = {
        'type': 'json',
        'auth': 'none',
        'methods': ['POST'],
    }

    """
    {
        "Host": "ventor-dev-integration-dev-161.odoo.com",
        "X-Forwarded-Host": "ventor-dev-integration-dev-161.odoo.com",
        "X-Forwarded-For": "83.217.94.198",
        "X-Forwarded-Proto": "https",
        "X-Real-Ip": "83.217.94.198",
        "Connection": "close",
        "Content-Length": "73",
        "Content-Type": "application/json"
        "Accept": "*/*",
        "Integration-Api-Key": "8c60bb92a2a7beb2a0fc399f0831d6d818a87412"
        "X-Magento2-Shop-Domain": "<magento store web address like a `your-maganto-shop.com`>",
        "X-Hook": "order_created"
    }
    """

    SHOP_NAME = 'X-Magento2-Shop-Domain'
    TOPIC_NAME = 'X-Hook'
    NEW_ORDER_METHOD_NAME = 'order_created'

    @property
    def integration_type(self):
        return MAGENTO_TWO

    @route(f'/<string:dbname>/integration/{MAGENTO_TWO}/<int:integration_id>/orders', **_kwargs)
    @build_environment
    @validate_integration
    def magento_two_receive_orders(self, *args, **kw):
        """
        Expected methods:
            order_created
            order_cancelled
        """
        _logger.info('Call magento2 webhook controller: magento_two_receive_orders()')
        integration = request.env['sale.integration'].browse(kw['integration_id'])
        return self._receive_order_generic(integration)

    @route(f'/<string:dbname>/integration/{MAGENTO_TWO}/<int:integration_id>/shipments', **_kwargs)
    @build_environment
    @validate_integration
    def magento_two_receive_shipments(self, *args, **kw):
        """
        Expected methods:
            shipment_created
        """
        _logger.info('Call magento2 webhook controller: magento_two_receive_shipments()')
        integration = request.env['sale.integration'].browse(kw['integration_id'])
        external_order_id = self._get_value_from_post_data('order_id')
        return self._receive_generic(integration, external_order_id)

    @route(f'/<string:dbname>/integration/{MAGENTO_TWO}/<int:integration_id>/invoices', **_kwargs)
    @build_environment
    @validate_integration
    def magento_two_receive_invoices(self, *args, **kw):
        """
        Expected methods:
            invoice_created
        """
        _logger.info('Call magento2 webhook controller: magento_two_receive_invoices()')
        integration = request.env['sale.integration'].browse(kw['integration_id'])
        external_order_id = self._get_value_from_post_data('order_id')
        return self._receive_generic(integration, external_order_id)

    def order_created(self, integration, external_order_id):
        """Order Created"""
        _logger.info('Call magento2 webhook controller: order_created()')
        return integration.integration_receive_orders_cron(cron_operation=False)  # TODO: by ID

    def order_cancelled(self, input_file):
        _logger.info('Call magento2 webhook controller method: order_cancelled()')
        post_data = self._get_post_data()
        data = {
            'integration_workflow_states': [post_data.get('status')],
        }
        return input_file._run_cancel_order(data)

    def shipment_created(self, input_file):
        _logger.info('Call magento2 webhook controller: shipment_created()')
        job_kwargs = input_file._get_job_actual_data_kwargs()
        job = input_file.with_delay(**job_kwargs).run_actual_pipeline()
        input_file.job_log(job)
        return job

    def invoice_created(self, input_file):
        _logger.info('Call magento2 webhook controller: invoice_created()')
        job_kwargs = input_file._get_job_actual_data_kwargs()
        job = input_file.with_delay(**job_kwargs).run_actual_pipeline()
        input_file.job_log(job)
        return job

    def _check_webhook_digital_sign(self, integration):
        headers = self._get_headers()
        token_from_header = headers[INTEGRATION_API_HEADER]
        token_from_odoo = request.env['res.config.settings'].get_integration_api_key()
        return token_from_header == token_from_odoo

    def _get_essential_headers(self):
        return [
            self.SHOP_NAME,
            self.TOPIC_NAME,
            INTEGRATION_API_HEADER,
        ]

    def verify_webhook(self, integration):
        name = integration.name
        # 1. Verify integration activation
        if not integration.is_active:
            return False, '%s integration is inactive.' % name

        # 2. Verify headers
        headers_ok = self.check_essential_headers()
        if not headers_ok:
            return False, '%s webhook invalid headers.' % name

        # 3. Verify forwarded host
        shop_domain = self.get_shop_domain(integration)
        settings_url = integration._truncate_settings_url()
        if settings_url not in shop_domain:
            return False, '%s webhook invalid shop domain "%s".' % (name, shop_domain)

        # Skipped 4, 5 steps in comparison to `super` method

        # 6. Verify webhook digital sign
        sign_ok = self._check_webhook_digital_sign(integration)
        if not sign_ok:
            return False, 'Wrong %s webhook digital signature.' % name

        return True, '%s: webhook has been verified.' % name
