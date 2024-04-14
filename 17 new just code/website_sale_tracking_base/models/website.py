# Copyright © 2021 Garazd Creation (<https://garazd.biz>)
# @author: Yurii Razumovskyi (<support@garazd.biz>)
# @author: Iryna Razumovska (<support@garazd.biz>)
# License OPL-1 (https://www.odoo.com/documentation/15.0/legal/licenses.html).

import json
import logging

from typing import Dict, List

from odoo import api, fields, models
from odoo.addons.sale.models.sale_order import SaleOrder
from .website_tracking_service import WebsiteTrackingService

_logger = logging.getLogger(__name__)

TRACKING_EVENT_TYPES = [
    ('lead', 'Lead'),
    ('login', 'Login'),
    ('sign_up', 'Sign Up'),
    ('view_product', 'View Product'),
    ('view_product_list', 'View Product List'),
    ('view_product_category', 'View Product Category'),
    ('search_product', 'Search Products'),
    ('add_to_wishlist', 'Add To Wishlist'),
    ('add_to_cart', 'Add To Cart'),
    ('begin_checkout', 'Begin Checkout'),
    ('add_shipping_info', 'Add Shipping Info'),
    ('add_payment_info', 'Add Payment Info'),
    ('purchase', 'Purchase'),
    ('purchase_portal', 'Order Sign on Portal'),
]


class Website(models.Model):
    _inherit = "website"

    tracking_is_active = fields.Boolean(string='Activate Tracking')
    tracking_is_logged = fields.Boolean(
        string='Logging',
        help='Log tracking events to a browser console.',
    )
    tracking_service_ids = fields.One2many(
        comodel_name='website.tracking.service',
        inverse_name='website_id',
        string='Tracking Services',
    )

    @api.model
    def _tracking_not_ecommerce_events(self) -> List:
        return ['lead', 'login', 'sign_up']

    @api.model
    def _tracking_event_mapping(self, service_type: str):
        """Return dictionary with mappings between event type and event name
        for specific type of tracking service. Method to override."""
        return {et[0]: et[0] for et in TRACKING_EVENT_TYPES}

    @api.model
    def _tracking_get_event_name(self, service_type: str, event_type: str):
        return self._tracking_event_mapping(service_type).get(event_type)

    def write(self, vals):
        """Deactivate logging when tracking is deactivated."""
        res = super(Website, self).write(vals)
        if 'tracking_is_active' in vals and not vals.get('tracking_is_active'):
            self.write({'tracking_is_logged': False})
        return res

    def _tracking_get_sale_order(self, order_id=None):
        self.ensure_one()
        return self.env['sale.order'].sudo().browse(order_id) if order_id else self.sale_get_order()

    def _tracking_get_currency(self, order=None, pricelist=None):
        self.ensure_one()
        return order.currency_id if order else pricelist.currency_id if pricelist else self.currency_id

    def _tracking_run_script(
            self,
            service: WebsiteTrackingService,
            product_data: List[Dict],
            order: SaleOrder,
            event_type: str,
    ) -> bool:
        """Determine to send tracking data to the tracking system or not."""
        self.ensure_one()
        website = self
        return bool(
           website and website.tracking_is_active
           and not self.env.user.has_group('base.group_user')
           and (product_data or order or event_type in self._tracking_not_ecommerce_events())  # flake8: noqa: E501
           and service.allow_send_data()
        )

    def _tracking_send_by_api_is_denied(self, service) -> bool:
        """Additional checks to send data via API or not. Method to override."""
        self.ensure_one()
        return False

    # pylint: disable-msg=too-many-branches
    # pylint: disable-msg=too-many-locals
    def _tracking_event_data(
            self,
            event_type: str,
            product_data: List[Dict] = None,
            pricelist_id: int = None,
            order_id: int = None,
            request_data: Dict = None,
    ) -> Dict:
        """Generate a data for event.

        :param event_type: one of the list "TRACKING_EVENT_TYPES" item
        :param product_data: list with product data
        :param pricelist_id: ID for the "product.pricelist" model
        :param order_id: ID of a record of the "sale.order" model
        :param request_data: custom data from HTTP request
        :return dict:
        """
        self.ensure_one()
        website = self
        event_data = {
            'error': None,
            'services': {},
        }
        # Sample of "event_data":
        # {
        #   'error': 'Error message',
        #   'services': {
        #       'ga4': [{
        #           'service_id': 15,
        #           'key': 1234500000,
        #           'event_name': 'add_to_cart',
        #           'run_script': True,
        #           'data': {},
        #           'user_data': {},
        #           'event_id: '205',  # Add a Log ID when the Internal Logging is on
        #       },
        #       {
        #           'service_id': 10,
        #           'key': 9999999999,
        #           'event_name': 'view_item',
        #           'run_script': False,
        #           'data': {},
        #           'user_data': {},
        #        }],
        #       'facebook': [{
        #           'service_id': 29,
        #           'key': 2233223322,
        #           'event_name': 'Purchase',
        #           'run_script': False,
        #           'data': {},
        #           'user_data': {'em': 'e6b1632a9d35d4bd44db02ec897ddc'},
        #       }],
        #   },
        # }

        # Check that the event type is proper
        if event_type not in [et[0] for et in TRACKING_EVENT_TYPES]:
            msg = "[Website Tracking] Unsupported event: %s" % event_type
            if website.tracking_is_logged:
                _logger.warning(msg)
            return {'error': msg}

        order = website._tracking_get_sale_order(order_id)
        pricelist = self.env['product.pricelist'].browse(pricelist_id)

        if event_type != 'login':
            visitor_sudo = self.env['website.visitor']._get_visitor_from_request(force_create=False)
        else:
            # A visitor can't be determined during login procedure.
            visitor_sudo = self.env['website.visitor'].sudo().browse()

        # Prefill tracking service data
        for service in website.tracking_service_ids:
            if not event_data['services'].get(service.type):
                event_data['services'][service.type] = []
            service_data = {
                'service_id': service.id,
                'key': service.key,
                'run_script': website._tracking_run_script(service, product_data, order, event_type),
                'data': {},
                'user_data': service.with_context(request_data=request_data).get_visitor_data(visitor_sudo.id, order.id),
            }
            event_data['services'][service.type].append(service_data)

        # Generate event data
        # pylint: disable-msg=unused-variable
        for service_type, service_datas in event_data.get('services', {}).items():
            for service_data in service_datas:
                service = self.env['website.tracking.service'].browse(service_data['service_id'])

                event_name = website._tracking_get_event_name(service.type, event_type)
                if event_name:
                    service_data.update({'event_name': event_name})
                else:
                    # Do not run script if the particular service doesn't have
                    # a specific event type
                    service_data.update({'run_script': False})

                # Get event data
                service_data['data'] = getattr(
                    service,
                    'get_data_for_' + event_type,
                )(product_data_list=product_data, order=order, pricelist=pricelist)

                # Complete data
                service_data['data'].update(service.get_common_data(
                    event_type=event_type,
                    product_data_list=product_data,
                    order=order,
                    pricelist=pricelist,
                ))

        # Internal Logging (only for public and portal users)
        if not self.env.user.has_group('base.group_user'):
            for service in website.tracking_service_ids.filtered('is_internal_logged'):
                # flake8: noqa: E501
                payload = [
                    data for data in event_data['services'].get(service.type)
                    if data['service_id'] == service.id
                ]
                log_data = {
                    'service_id': service.id,
                    'event_type': event_type,
                    'payload': payload and json.dumps(payload[0]) or '',
                    'order_id': order.id,
                    'product_ids': [(4, p['product_id']) for p in product_data],
                    'search_term': self._context.get('search_term', ''),
                    'url': request_data.get('url'),
                    'visitor_id': visitor_sudo.id,
                    'country_id': visitor_sudo.country_id.id,
                }
                # Add website visitor data
                log_data.update({
                    'user_agent': service.track_user_agent and request_data.get('user_agent'),
                    'user_ip_address': service.track_ip_address and request_data.get('ip'),
                })

                # Add extra data by services
                log_data.update(service.extra_log_data())

                # Additional checks before sending via API
                api_send_is_denied = website._tracking_send_by_api_is_denied(service=service)
                log_data.update({'api_send_is_denied': api_send_is_denied})
                if api_send_is_denied:
                    log_data.update({'state': 'internal'})

                # Create only logs that are supported by the current service
                if website._tracking_get_event_name(service.type, event_type):
                    log = self.env['website.tracking.log'].sudo().create(log_data)

                    # Add a log ID as "event_id" in the event data
                    payload[0]['event_id'] = str(log.id)

                # Post-processing of the "data" param
                payload[0]['data'].update(service.post_processed_data(payload[0]))

        # System Logging
        if website.tracking_is_logged:
            _logger.debug('[Website Tracking] Event Data: %s', event_data)

        return event_data
