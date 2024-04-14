# See LICENSE file for full copyright and licensing details.

import base64
import itertools
import json
import logging
import mimetypes

from io import BytesIO
from copy import deepcopy
from datetime import datetime
from collections import Counter, defaultdict

from odoo.api import _
from odoo.exceptions import UserError

from odoo.addons.integration.tools import IS_FALSE, IS_TRUE
from odoo.addons.integration.tools import TemplateHub, add_dynamic_kwargs
from odoo.addons.integration.api.abstract_apiclient import AbsApiClient
from odoo.addons.integration.models.fields.common_fields import GENERAL_GROUP

from .tools import XmlRpc, WooOrder
from .client.exceptions import WooCommerceApiException
from .client.wordpress_client import WordPressClient
from .client.woocommerce_client import WooCommerceClient, MAX_PAGE_SIZE


_logger = logging.getLogger(__name__)

WOOCOMMERCE = 'woocommerce'
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
META_DATA = 'meta_data'

# Order statuses
ORDER_STATUS_PENDING = 'pending'
ORDER_STATUS_FAILED = 'failed'
ORDER_STATUS_PROCESSING = 'processing'
ORDER_STATUS_COMPLETED = 'completed'
ORDER_STATUS_ON_HOLD = 'on-hold'
ORDER_STATUS_CANCELLED = 'cancelled'
ORDER_STATUS_REFUNDED = 'refunded'
ORDER_STATUSES = {
    ORDER_STATUS_PENDING: (
        'Pending payment',
        'Order received, no payment initiated. Awaiting payment (unpaid).',
    ),
    ORDER_STATUS_FAILED: (
        'Failed',
        'Payment failed or was declined (unpaid) or requires authentication (SCA). '
        'Note that this status may not show immediately and instead show as Pending '
        'until verified (e.g., PayPal).',
    ),
    ORDER_STATUS_PROCESSING: (
        'Processing',
        'Payment received (paid) and stock has been reduced; order is awaiting fulfillment. '
        'All product orders require processing, except those that only contain products which '
        'are both Virtual and Downloadable.',
    ),
    ORDER_STATUS_COMPLETED: (
        'Completed',
        'Order fulfilled and complete - requires no further action.',
    ),
    ORDER_STATUS_ON_HOLD: (
        'On hold',
        'Awaiting payment - stock is reduced, but you need to confirm payment.',
    ),
    ORDER_STATUS_CANCELLED: (
        'Canceled',
        'Canceled by an admin or the customer - stock is increased, no further action required.',
    ),
    ORDER_STATUS_REFUNDED: (
        'Refunded',
        'Refunded by an admin - no further action required.',
    ),
}

# Product types
SIMPLE = 'simple'
GROUPED = 'grouped'
EXTERNAL = 'external'
VARIABLE = 'variable'

# Product statuses
STATUS_DRAFT = 'draft'
STATUS_PENDING = 'pending'
STATUS_PRIVATE = 'private'
STATUS_PUBLISH = 'publish'

# WooCommerce endpoints
ATTRIBUTE = 'products/attributes/%s'
ATTRIBUTES = 'products/attributes'
ATTRIBUTE_VALUE = 'products/attributes/%s/terms/%s'
ATTRIBUTE_VALUES = 'products/attributes/%s/terms'
COUNTRIES = 'data/countries'
CUSTOMER = 'customers/%s'
CUSTOMERS = 'customers'
CATEGORY = 'products/categories/%s'
CATEGORIES = 'products/categories'
ORDER = 'orders/%s'
ORDERS = 'orders'
PAYMENT_GATEWAY = 'payment_gateways/%s'
PAYMENT_GATEWAYS = 'payment_gateways'
PRODUCT = 'products/%s'
PRODUCTS = 'products'
SYSTEM_STATUS = 'system_status'
SHIPPING_METHODS = 'shipping_methods'
SHIPPING_ZONES = 'shipping/zones'
SHIPPING_ZONES_METHODS = 'shipping/zones/%s/methods'
TAG = 'products/tags/%s'
TAGS = 'products/tags'
TAX_CLASS = 'taxes/classes/%s'
TAX_CLASSES = 'taxes/classes'
TAX = 'taxes/%s'
TAXES = 'taxes'
VARIATION = 'products/%s/variations/%s'
VARIATIONS = 'products/%s/variations'
WEBHOOK = 'webhooks/%s'
WEBHOOKS = 'webhooks'
WEIGHT_UOM = 'settings/products/woocommerce_weight_unit'

# WordPress endpoints
MEDIA = 'media/%s'
MEDIAS = 'media'

PLUGIN_WPMLST = 'wpml-string-translation'


class WooCommerceApiClient(AbsApiClient):
    default_receive_orders_filter = (
        '{"status": "<put state id here>"}'
    )

    settings_fields = (
        ('url', 'Shop URL', ''),
        ('admin_url', 'Admin URL', ''),
        ('consumer_key', 'Consumer Key', ''),
        ('consumer_secret', 'Consumer Secret', '', False, True),
        ('verify_ssl', 'Verify SSL', 'True', True),
        ('wc_api_version', 'WooCommerce API Version', 'wc/v3'),
        ('wp_api_version', 'WordPress API Version', 'wp/v2'),
        ('wp_user', 'WordPress User', ''),
        ('wp_app_password', 'WordPress Application Password', '', False, True),
        ('language_id', 'Shop Language Code', ''),
        (
            'import_products_filter',
            'Import Products Filter',
            '{"type": "simple,external,variable"}'
        ),
        (
            'receive_orders_filter',
            'Receive Orders Filter',
            default_receive_orders_filter,
            True,
        ),
        (
            'weight_uom',
            (
                'WooCommerce weight unit.'
                ' Will be automatically populated when integration is active'
            ),
            '',
        ),
        ('adapter_version', 'Version number of the api client', '0'),
        ('decimal_precision', 'Number of decimal places in the price of the exported product', '2'),
    )

    _api_unique_fields = [
        'sku',
    ]

    def __init__(self, settings):
        super().__init__(settings)

        self._settings = settings
        self._client = WooCommerceClient(settings)
        self._wp_client = WordPressClient(settings)

        self.admin_url = self.get_settings_value('admin_url')
        self._weight_uom = self.get_settings_value('weight_uom')

        self._active_plugins = []

        self._locale = ''
        self._accept_translations = None
        self._lang = self.get_settings_value('language_id')

        self._accept_bundles = None
        self._accept_composites = None

        self._update_adapter_properties()

    @property
    def lang(self):
        if self._lang:
            return self._lang
        return self.locale.split('_', maxsplit=1)[0]

    @property
    def locale(self):  # TODO: do the math if the 'lang' property don't suite for the `locale`
        return self._locale

    @property
    def accept_translations(self):
        return self._accept_translations

    @property
    def accept_nested_products(self):
        return self._accept_bundles or self._accept_composites

    def prepare_lang_param(self):
        return dict(lang=self.lang)

    def _update_adapter_properties(self):
        # Don't use the `fetch_one` method in order to see real traceback
        shop_env = self.get(SYSTEM_STATUS)[0]

        self._active_plugins = [
            x['plugin'].split('/', maxsplit=1)[0] for x in shop_env['active_plugins']
        ]

        self._locale = shop_env['environment']['language']
        self._accept_translations = (PLUGIN_WPMLST in self._active_plugins)

        self._accept_bundles = ('woocommerce-product-bundles' in self._active_plugins)
        self._accept_composites = ('woocommerce-composite-products' in self._active_plugins)

    def get_weight_uom_for_converter(self):
        if not self._weight_uom:
            raise UserError(_(
                'Sale Integration setting "WooCommerce weight unit" is not specified. '
                'Please, deactivate and then activate Sale Integration to populate it'))

        return self._weight_uom

    def get_weight_uoms(self):
        if self._weight_uom:
            return [self._weight_uom]

        return []

    def get(self, endpoint, **kwargs):
        return self._client.get(endpoint, **kwargs)

    def fetch_one(self, endpoint, params=None):
        return self._client.fetch_one(endpoint, params=params)

    def fetch_list(self, endpoint, params=None):
        return self._client.get(endpoint, params=params)

    def create_obj(self, endpoint, data, **kwargs):
        return self._client.create_obj(endpoint, data, **kwargs)

    def update(self, endpoint, data, **kwargs):
        return self._client.update(endpoint, data, **kwargs)

    def update_batch(self, endpoint, data, **kwargs):
        return self._client.update_batch(endpoint, data, **kwargs)

    def delete_batch(self, endpoint, data, **kwargs):
        return self._client.delete_batch(endpoint, data, **kwargs)

    def delete(self, endpoint, **kwargs):
        _logger.info(f'WooCommerce: delete external object "{endpoint}"')
        return self._client.delete(endpoint, **kwargs)

    def get_shop_env(self):
        return self.fetch_one(SYSTEM_STATUS)

    def check_connection(self):
        _logger.info('WooCommerce: check_connection()')
        system_status = self.get_shop_env()  # TODO: A little bit weird way
        return bool(system_status)

    def get_api_resources(self):
        # WC has access only for write and read for all entities
        _logger.info('WooCommerce: get_api_resources(). Not implemented.')
        return

    @add_dynamic_kwargs
    def get_delivery_methods(self, **kw):
        _logger.info('WooCommerce: get_delivery_methods()')
        delivery_methods = []

        # Get the list of shipping methods
        shipping_methods = self.get(SHIPPING_METHODS)
        for method in shipping_methods:
            delivery_methods.append({
                'id': str(method['id']),
                'name': str(method['title']),
            })

        # Get the list of shipping zones from WooCommerce
        shipping_zones = self.get(SHIPPING_ZONES)

        for zone in shipping_zones:
            zone_id = str(zone['id'])
            zone_name = zone['name']

            # Get the list of shipping methods for the current zone
            shipping_methods = self.get(SHIPPING_ZONES_METHODS % zone_id)

            for method in shipping_methods:
                delivery_methods.append({
                    'id': str(method['instance_id']),
                    'name': '{} ({})'.format(method['title'], zone_name),
                })

        return delivery_methods

    def get_single_tax(self, tax_id):
        taxes = self.get_taxes()
        tax_list = [x for x in taxes if x['id'] == tax_id]
        return tax_list and tax_list[0] or dict()

    def get_taxes(self):
        """
        :return:
            [
                {'id': '1',
                 'rate': '5.000',
                 'name': 'CA 5%',
                 'tax_groups': [{'id': '6', 'name': 'CA Standard Rate'}]
                 },
                 {'id': '3',
                  'rate': '0.000',
                  'name': 'CA-MB 8%',
                  'tax_groups': [{'id': '6', 'name': 'CA Standard Rate'}]
                 },
                 ...
            ]
        """
        _logger.info('WooCommerce: get_taxes()')

        def get_tax_group(tax_class):
            if tax_groups.get(tax_class):
                return [{'id': tax_class, 'name': tax_groups.get(tax_class)}]
            else:
                return []

        tax_group_response = self.get(TAX_CLASSES)
        tax_groups = {x['slug']: x['name'] for x in tax_group_response}

        tax_response = self.get(TAXES)

        tax_response = [tax for tax in tax_response if tax['rate'].strip()]

        return [
            {
                'id': str(x['id']),
                'rate': x['rate'],
                'name': self._format_tax(x),
                'tax_groups': get_tax_group(x['class']),
            }
            for x in tax_response
        ]

    @staticmethod
    def _format_tax(tax):
        tax_name = f"{tax['name']} ({tax['country']}"
        if tax.get('state') or tax['state'] == '*':
            tax_name += f"-{tax['state']}"
        tax_name += f" {tax['rate']}%)"

        return tax_name

    def get_payment_methods(self):
        _logger.info('WooCommerce: get_payment_methods()')
        payment_gateways = self.get(PAYMENT_GATEWAYS)
        return [
            {
                'id': str(x['id']),
                'name': x['title'],
            }
            for x in payment_gateways
        ]

    def get_languages(self):
        _logger.info('WooCommerce: get_languages()')

        if self.accept_translations:
            return self._fetch_langs_from_wpml()

        # Return default WordPress language
        lang = self.locale.split('_', maxsplit=1)[0]
        return [dict(id=lang, name=self.locale, external_reference=self.locale)]

    def _fetch_langs_from_wpml(self):
        """Get languages added with WPML plugin"""

        user = self.get_settings_value('wp_user')
        password = self.get_settings_value('wp_app_password')

        if not user or not password:
            raise UserError(_(
                'Fill out the required fields "WordPress User" and "WordPress User '
                'Application Password" with the help of "Quick Configuration" wizard.'
            ))

        endpoint = self._get_xmlrpc_endpoint()
        response = XmlRpc.send_request(endpoint, 'wpml.get_languages', [IS_TRUE, user, password])

        if not response.ok:
            raise UserError(f'{response.url}. {response.text}')

        try:
            response_dict = XmlRpc.xml_string_to_dict(response.text, root_tag='struct')
            lang_list = self._parse_languages(response_dict)
        except Exception as ex:
            raise UserError(ex.args[0])

        return [dict(id=code, name=name, external_reference=ref) for code, name, ref in lang_list]

    @staticmethod
    def _parse_languages(member_list):
        """
        :return:
            [
                ('en', 'English', 'en_GB'),
                ('ku', 'Kurdish', 'ckb'),
                ('pl', 'Polish', 'pl_PL'),
                ('ru', 'Russian', 'ru_RU'),
            ]
        """
        result = list()
        for member in member_list:
            data = dict()
            value_list = member['member'][-1]['value'][0]['struct']

            for child in value_list:
                dict_name, dict_value = child['member']
                key = dict_name['name']
                value = dict_value['value'][0]['string']
                data[key] = value

            result.append(
                (data['code'], data['english_name'], data['default_locale']),
            )
        return result

    def _get_xmlrpc_endpoint(self):
        url = self.get_settings_value('url')

        while url.endswith('/'):
            url = url[:-1]

        if url.endswith('index.php'):
            url = url.replace('index.php', '')

        while url.endswith('/'):
            url = url[:-1]

        return f'{url}/xmlrpc.php'

    def get_attributes(self):
        _logger.info('WooCommerce: get_attributes()')
        attributes = self.get(ATTRIBUTES)
        return [
            {
                'id': str(x['id']),
                'name': x['name'],
            }
            for x in attributes
        ]

    def get_attribute_values(self):
        _logger.info('WooCommerce: get_attribute_values()')
        result = []

        for attribute in self.get_attributes():
            terms = self.get(ATTRIBUTE_VALUES % attribute['id'])
            result += [
                {
                    'id': x['id'],
                    'name': x['name'],
                    'id_group': attribute['id'],
                } for x in terms
            ]

        return result

    def get_features(self):
        _logger.info('WooCommerce: get_features()')
        return [{
            'id': GENERAL_GROUP,
            'name': 'General group',
        }]

    def get_feature_values(self):
        _logger.info('WooCommerce: get_feature_values()')
        tags = self.get(TAGS)
        return [
            {
                'id': x['id'],
                'name': x['name'],
                'id_group': GENERAL_GROUP,
            } for x in tags
        ]

    def get_countries(self):
        _logger.info('WooCommerce: get_countries()')

        wc_countries = self.get(COUNTRIES)

        return [
            {
                'id': wc_country['code'],
                'name': wc_country['name'],
                'external_reference': wc_country['code'],
            }
            for wc_country in wc_countries
        ]

    def get_states(self):
        _logger.info('WooCommerce: get_states()')
        wc_countries = self.get(COUNTRIES)
        result = []

        for wc_country in wc_countries:
            result.extend([
                {
                    'id': f'{wc_country["code"]}_{wc_state["code"]}',
                    'name': wc_state['name'],
                    'external_reference': f'{wc_country["code"]}_{wc_state["code"]}',
                }
                for wc_state in wc_country['states']
            ])

        return result

    def get_categories(self):
        _logger.info('WooCommerce: get_categories()')
        categories = self.get(CATEGORIES, params=self.prepare_lang_param())

        result = list()
        for category in categories:
            data = self._get_fields_with_translations(CATEGORY, category, ['name'])

            result.append({
                'name': data['name'],
                'id': str(category['id']),
                'id_parent': str(category['parent']),
            })

        return result

    def get_sale_order_statuses(self):
        _logger.info('WooCommerce: get_sale_order_statuses()')
        order_states = list()

        for state, values in ORDER_STATUSES.items():
            order_states.append({
                'id': state,
                'name': values[0],
                'external_reference': False,
            })

        return order_states

    def _get_product_filter(self, search_filter=None):
        kwargs = search_filter or dict()
        import_products_filter = json.loads(self.get_settings_value('import_products_filter'))
        product_filter_dict = {
            **self.prepare_lang_param(),
            **import_products_filter,
            **kwargs,
        }
        return product_filter_dict

    def _get_products(self, params):
        result = []
        product_types = [False]
        params['orderby'] = 'id'  # TODO: make it by default for the all requests

        if 'type' in params:
            product_types = params['type'].split(',')
            product_types = [x.strip() for x in product_types]

        for product_type in product_types:
            if product_type:
                params['type'] = product_type

            product_list = self.get(endpoint=PRODUCTS, params=params)
            result.extend(product_list)

        return result

    def get_product_template_ids(self):
        _logger.info('WooCommerce: get_product_template_ids()')
        product_filter = self._get_product_filter()
        templates = self._get_products(product_filter)

        return [x['id'] for x in templates]

    @add_dynamic_kwargs
    def get_product_templates(self, template_ids, **kw):
        _logger.info('WooCommerce: get_product_templates()')
        product_filter = self._get_product_filter({'include': ','.join(template_ids)})
        products = self._get_products(product_filter)  # TODO: lang?

        env = self._get_env(kw)
        integration = self._get_integration(kw)
        barcode_field = integration._get_product_barcode_name()
        ecommerce_barcode = integration._template_field_name_to_ecommerce_name(barcode_field)

        result = {
            str(product['id']): {
                'id': str(product['id']),
                'name': product['name'],
                'barcode': product.get(ecommerce_barcode) or None,
                'external_reference': product.get('sku') or None,
                'variants': [],
            }
            for product in products
        }

        AttributeValue = env['product.attribute.value']
        for product_id in [x['id'] for x in products if x['type'] == VARIABLE]:
            product_id = str(product_id)
            variants = self.get(VARIATIONS % product_id)

            for variant in variants:
                external_values = [
                    AttributeValue._find_external_by_name(
                        integration, str(x['id']), str(x['option']),
                    )
                    for x in variant['attributes']
                ]
                result[product_id]['variants'].append({
                    'id': self._build_product_external_code(product_id, variant['id']),
                    'name': result[product_id]['name'],
                    'external_reference': variant.get('sku') or None,
                    'ext_product_template_id': product_id,
                    'barcode': variant.get(ecommerce_barcode) or None,
                    'attribute_value_ids': [x.code for x in filter(None, external_values)],
                })

        return result

    def get_customer_by_pages(self, date_since, page):
        customers = self.get(
            endpoint=CUSTOMERS,
            page=page,
            limit=MAX_PAGE_SIZE,
            params={
                'per_page': MAX_PAGE_SIZE,
                'orderby': 'registered_date',
                'order': 'desc',
            }
        )

        if date_since:
            customers = list(filter(
                lambda x: datetime.strptime(x['date_created_gmt'], DATETIME_FORMAT) > date_since,
                customers,
            ))

        return [
            {
                'customer': self._parse_customer(customer),
                'shipping': self._parse_address(customer, customer['shipping'], 'delivery'),
                'billing': self._parse_address(customer, customer['billing'], 'invoice'),
            }
            for customer in customers
        ]

    def get_customer_ids(self, date_since=None):
        # For import customers used get_customer_by_pages
        _logger.info('WooCommerce: get_customer_ids(). Not implemented.')
        return

    def get_customer_and_addresses(self, customer_id):
        _logger.info('WooCommerce: get_customer_and_addresses()')
        customer_data = self.fetch_one(CUSTOMER % customer_id)

        if not customer_data:
            return {}, {}

        customer = self._parse_customer(customer_data)
        addresses = (
            self._parse_address(customer_data, customer_data['shipping'], 'delivery'),
            self._parse_address(customer_data, customer_data['billing'], 'invoice'),
        )

        return customer, addresses

    def get_locations(self):
        _logger.info('WooCommerce: get_locations(). Not Implemented.')
        return []

    def get_pricelists(self):
        _logger.info('WooCommerce: get_pricelists(). Not implemented.')
        return []

    @add_dynamic_kwargs
    def order_fetch_kwargs(self, **kw):
        filters = self.get_settings_value('receive_orders_filter')
        integration = self._get_integration(kw)
        receive_from = integration.last_receive_orders_datetime_str
        cut_off_datetime = integration.orders_cut_off_datetime_str

        options = {
            'lang': 'all',
            'dates_are_gmt': 'true',
            'modified_after': receive_from,
            'orderby': 'modified',
            'order': 'asc',
        }

        if cut_off_datetime:
            options['created_after'] = cut_off_datetime

        options.update(filters)
        return {
            'params': options,
            'limit': self.order_limit_value(),
        }

    @add_dynamic_kwargs
    def receive_orders(self, **kw):
        _logger.info('WooCommerce: receive_orders()')

        kwargs = self.order_fetch_kwargs()(**kw)
        orders = self.get(ORDERS, **kwargs)

        result = list()
        for order in orders:
            vals = dict(
                id=str(order['id']),
                data=order,
                updated_at=order['date_modified_gmt'],
                created_at=order['date_created_gmt'],
            )
            result.append(vals)

        return result

    def receive_order(self, order_id):
        _logger.info('WooCommerce: receive_order()')
        input_file = dict()
        order = self.fetch_one(ORDER % order_id, params=self.prepare_lang_param())

        if not order:
            return input_file

        input_file['id'] = str(order['id'])
        input_file['data'] = order
        return input_file

    def get_order_class_parser(self):
        """Hook for external module extensions"""
        return WooOrder

    @add_dynamic_kwargs
    def parse_order(self, input_file, **kw):
        ClassParser = self.get_order_class_parser()
        woo_order = ClassParser(self._get_integration(kw), input_file)
        return woo_order.parse()

    def validate_template(self, template):
        _logger.info('WooCommerce: validate_template().')
        mappings_to_delete = []

        # (1) if template with such external id exists?
        external_template_id = template['external_id']
        if external_template_id:
            external_template = self._client.fetch_one(PRODUCT % external_template_id)

            if not external_template:
                mappings_to_delete.append({
                    'model': 'product.template',
                    'external_id': external_template_id,
                })

        # (2) if part of the variants has no external_id?
        mappings_to_update = self.parse_mappings_to_update(template['products'])

        # (3) if variant with such external id exists?
        for variant in template['products']:
            complex_variant_id = variant['external_id']
            if not complex_variant_id:
                continue

            external_template_id, external_variant_id = self._parse_product_external_code(
                complex_variant_id,
            )
            if not external_variant_id:
                continue

            external_variant = self._client.fetch_one(
                VARIATION % (external_template_id, external_variant_id),
            )
            if not external_variant:
                mappings_to_delete.append({
                    'model': 'product.product',
                    'external_id': complex_variant_id,
                })

        return mappings_to_delete, mappings_to_update

    @add_dynamic_kwargs
    def find_existing_template(self, template, **kw):
        _logger.info('WooCommerce: find_existing_template().')
        # we try to search existing product template ONLY if there is no external_id for it
        # If there is external ID then we already mapped products and we do not need to search
        if template['external_id']:
            return False

        odoo_variants = list(filter(lambda x: x['attribute_values'], template['products']))

        # Now let's validate if there are no duplicated references in WooCommerce
        variant_skus = [x['fields']['sku'] for x in template['products']]

        # Let's validate if all found products belong to the same product template
        ext_variants = self.get(PRODUCTS, params={'sku': ','.join(variant_skus)})

        # if parent_id - it mean variant, if id - product
        ids_set = set([str(x['parent_id'] or x['id']) for x in ext_variants])

        # If nothing found, then just return False
        if len(ids_set) == 0:
            return False

        # If more than one product id found - then we found references,
        # but they all belong to different products and we need to inform user about it
        # So he can fix on Magento side
        # Because in Odoo it is single product template, and in Magento - separate
        # product templates. That should not be allowed. Note that after previous check on
        # duplicates most likely it will not be possible, this check is just to be 100% sure
        if len(ids_set) > 1:
            raise UserError(_('Product reference(s) "%s" were found in multiple WooCommerce '
                              'Products: %s. This is not allowed as in Odoo same references'
                              ' already belong to single product template and its variants. '
                              'Structure of Odoo products and WooCommerce Products should be '
                              'the same!') % (', '.join(variant_skus), ', '.join(list(ids_set))))

        ext_template_id = list(ids_set)[0]

        # Check if products in Odoo has the same amount of variants as in Magento
        ext_variants = self.get(VARIATIONS % ext_template_id)

        if len(odoo_variants) != len(ext_variants):
            integration = self._get_integration(kw)

            raise UserError(
                _('Amount of combinations in WooCommerce is %d. While amount in Odoo is %d. '
                  'Please, check the product with id %s in WooCommerce and make sure it has '
                  'the same amount of combinations as variants in Odoo (with enabled integration '
                  '"%s")') % (
                    len(ext_variants),
                    len(odoo_variants),
                    ext_template_id,
                    integration
                )
            )

        if not ext_variants:
            return ext_template_id

        for ext_variant in ext_variants:
            # Make sure that reference is set on the ext_variant
            reference = ext_variant['sku']

            if not reference:
                raise UserError(_('Product with id "%s" do not have references on '
                                  'all variations. Please, add them and relaunch '
                                  'product export') % ext_template_id)

            # List of WooCommerce attributes
            attribute_values_from_woocommerce = self.parse_custom_attributes(ext_variant)
            attribute_values_from_woocommerce = [str(x) for x in attribute_values_from_woocommerce]

            # List of Odoo attributes
            odoo_variant = list(
                filter(lambda x: x['fields']['sku'] == reference, template['products']))

            if len(odoo_variant) == 0:
                error_message = \
                    _('There is no variant in Odoo with reference "%s" that corresponds to '
                      'WooCommerce product %s') % (reference, ext_template_id)
                raise UserError(error_message)

            attribute_values_from_odoo = [
                x['external_id'] for x in odoo_variant[0]['attribute_values']
            ]

            if Counter(attribute_values_from_odoo) != Counter(attribute_values_from_woocommerce):
                raise UserError(
                    _('WooCommerce Variant with reference %s has variant values %s. While same '
                      'Odoo Variant has attribute values %s. Products in WooCommerce and Odoo '
                      'with the same reference should have the same combination of attributes.')
                    % (
                        reference,
                        attribute_values_from_woocommerce,
                        attribute_values_from_odoo,
                    )
                )

        return ext_template_id

    def export_template(self, template_data):
        _logger.info('WooCommerce: export_template().')
        mappings = []

        template = self._update_or_create_template(template_data)
        external_template_id = str(template['id'])

        mappings.append({
            'model': 'product.template',
            'id': template_data['id'],
            'external_id': external_template_id,
        })

        if len(template_data['products']) == 1:
            template_data['products'][0]['fields'].pop('sku')

        for variant_data in template_data['products']:
            external_variant_id = self._update_or_create_variant(external_template_id, variant_data)

            complex_variant_id = self._build_product_external_code(
                external_template_id,
                external_variant_id,
            )
            mappings.append({
                'model': 'product.product',
                'id': variant_data['id'],
                'external_id': complex_variant_id,
            })

        return mappings

    def _update_or_create_template(self, template_data):
        # 0. Prepare payload data
        data = self._prepare_template_payload(template_data)

        # 1. Create or update external template
        template_external_id = template_data['external_id']
        if not template_external_id:
            template_created = self.create_obj(PRODUCTS, data)

            if self.accept_translations:
                self._send_product_translations(
                    str(template_created['id']),
                    template_data,
                    template_created['translations'],
                )

            return template_created

        template = self.fetch_one(
            PRODUCT % template_external_id,
            params=self.prepare_lang_param(),
        )

        # 2. Removes inactive internal variant-associated external variants from a template.
        odoo_variant_set = set()
        for variant_data in template_data['products']:
            complex_variant_id = variant_data.get('external_id')
            if not complex_variant_id:
                continue
            __, external_variant_id = self._parse_product_external_code(complex_variant_id)
            if external_variant_id:
                odoo_variant_set.add(int(external_variant_id))

        external_variant_set = {int(x) for x in template['variations']}
        missing_variant_ids = external_variant_set - odoo_variant_set
        for external_variant_id in missing_variant_ids:
            self.delete(VARIATION % (template_external_id, external_variant_id))

        # 3. Update external template
        if data.get('status') == STATUS_PUBLISH and template['status'] == STATUS_PRIVATE:
            data['status'] = STATUS_PRIVATE

        template_updated = self.update(PRODUCT % template_external_id, data)

        if self.accept_translations:
            self._send_product_translations(
                template_external_id,
                template_data,
                template_updated['translations'],
            )

        return template_updated

    def _update_or_create_variant(self, external_template_id, variant_data):
        # 0. Check for having external variant
        attribute_values = variant_data['attribute_values']
        if not attribute_values:
            return IS_FALSE

        external_variant_id = None
        complex_variant_id = variant_data['external_id']

        if complex_variant_id:
            __, external_variant_id = self._parse_product_external_code(complex_variant_id)
            if not external_variant_id:
                return IS_FALSE

        # 1. Prepare payload data
        data = self._prepare_converted_fields(variant_data['fields'], self.lang)
        data['attributes'] = []

        for value in attribute_values:
            external_attr_id = value['attribute']

            external_attr_value = self.fetch_one(
                ATTRIBUTE_VALUE % (external_attr_id, value['external_id']),
            )

            data['attributes'].append({
                'id': int(external_attr_id),
                'option': external_attr_value['name'],
            })

        # 2. Update or create external variant
        if external_variant_id:
            variant = self.update(VARIATION % (external_template_id, external_variant_id), data)
            return variant['id']

        variant = self.create_obj(VARIATIONS % external_template_id, data)
        return variant['id']

    def _parse_translated_value(self, field_value_dict, lang=None):
        target_lang = lang or self.lang
        translations = field_value_dict['language']
        return translations.get(target_lang) or str()

    def _prepare_converted_fields(self, fields_dict, lang, translation_only=False):
        result = dict()

        for field_name, field_value in fields_dict.items():

            # 1. Handle meta fields (include translations)
            if field_name == META_DATA:
                meta_data_list = list()

                for data in field_value:
                    data_copy = deepcopy(data)
                    data_value = data['value']

                    if self._is_translated_field(data_value):
                        data_value_tr = self._parse_translated_value(data_value, lang=lang)
                        data_copy['value'] = data_value_tr

                    meta_data_list.append(data_copy)

                if not meta_data_list:
                    continue

                value = meta_data_list

            # 2. Handle translatable fields
            elif self._is_translated_field(field_value):
                value = self._parse_translated_value(field_value, lang=lang)

            # 3. Handle simple fields
            else:
                if translation_only and (field_name in self._api_unique_fields):
                    continue

                value = field_value

            result[field_name] = value

        if self.accept_translations:
            result['lang'] = lang

        return result

    def _prepare_template_payload(self, template_data):
        data = self._prepare_converted_fields(template_data['fields'], self.lang)

        data.update(
            type=SIMPLE,
            virtual=False,
            attributes=template_data['attributes'],
        )

        if template_data['type'] == 'service':
            data['virtual'] = True
        elif template_data['products'] and template_data['products'][0]['attribute_values']:
            data['type'] = VARIABLE
        elif template_data['kits']:
            data['type'] = GROUPED

        return data

    def _send_product_translations(self, external_product_id, product_data, existing_translations):
        """
        :params:
            'existing_translations': {
                'en': '1622',
                'pl': '1813'
            }
        """
        result, fields_dict = dict(), product_data['fields']

        for code in product_data['langs']:
            if code == self.lang:
                continue

            data = self._prepare_converted_fields(fields_dict, code, translation_only=True)

            if code in existing_translations:
                external_id = existing_translations[code]
                self.update(PRODUCT % external_id, data)
                result[code] = external_id
            else:
                data['translation_of'] = external_product_id
                template_created_tr = self.create_obj(PRODUCTS, data)
                result[code] = str(template_created_tr['id'])

        _logger.info(f'{self._integration_name}: updated translations {str(result)}')
        return result

    def export_images(self, images):
        _logger.info('WooCommerce: export_images()')
        result = dict()
        template_images_data = images['template']

        external_template_id = template_images_data['id']
        upd_images = template_images_data['default'] and [template_images_data['default']] or list()
        upd_images.extend(template_images_data['extra'])

        export_result = self._export_images(PRODUCT % external_template_id, 'images', upd_images)

        result[external_template_id] = export_result

        for variant_images_data in images['products']:
            complex_variant_id = variant_images_data['id']
            external_template_id, external_variant_id = self._parse_product_external_code(
                complex_variant_id,
            )
            if not external_variant_id:
                continue

            endpoint = VARIATION % (external_template_id, external_variant_id)

            export_result = self._export_images(endpoint, 'image', variant_images_data['default'])
            result[complex_variant_id] = export_result

        return result

    def _export_images(self, endpoint, field, images_data):
        odoo_images = isinstance(images_data, list) and images_data or [images_data]
        upd_images = list()
        result = list()

        for odoo_image in odoo_images:
            if not odoo_image:
                continue

            external_image_id = odoo_image['external_image_id']

            if external_image_id and not self._wp_client.fetch_one(MEDIA % external_image_id):
                external_image_id = False

            if not external_image_id:
                data = base64.b64decode(odoo_image['data'])
                extension = mimetypes.guess_extension(odoo_image['mimetype'])
                file_name = odoo_image['product_name'] + extension

                external_image = self._wp_client.create_obj(
                    MEDIAS,
                    data=BytesIO(data),
                    headers={
                        'Content-Type': odoo_image['mimetype'],
                        'Content-Disposition': f'attachment; filename={file_name}',
                    }
                )

                if external_image:
                    external_image_id = external_image['id']

            if external_image_id:
                upd_images.append({'id': int(external_image_id)})

            result.append({
                'odoo_obj_name': odoo_image['odoo_obj_name'],
                'odoo_obj_id': odoo_image['odoo_obj_id'],
                'odoo_obj_field_name': odoo_image['odoo_obj_field_name'],
                'external_image_id': str(external_image_id),
            })

        if not isinstance(images_data, list):
            upd_images = upd_images and upd_images[0] or None

        self.update(endpoint, {field: upd_images})

        return result

    def export_attribute(self, attribute):
        _logger.info('WooCommerce: export_attribute().')

        wc_attribute = self.create_obj(
            endpoint=ATTRIBUTES,
            data={
                'name': attribute['name'],
                'type': 'select',
            }
        )

        return wc_attribute['id']

    def export_attribute_value(self, attribute_value):
        _logger.info('WooCommerce: export_attribute_value().')
        attribute_id = attribute_value['attribute']

        wc_attribute_value = self.create_obj(
            endpoint=ATTRIBUTE_VALUES % attribute_id,
            data={'name': attribute_value['name']}
        )

        return wc_attribute_value['id']

    def export_feature(self, feature):
        # WC Hasn't features. Except it we create Tags
        _logger.info('WooCommerce: export_feature(). Not implemented.')
        return

    def export_feature_value(self, feature_value):
        _logger.info('WooCommerce: export_feature_value().')
        wc_tag = self.create_obj(TAGS, data={'name': feature_value['name']})

        return wc_tag['id']

    def export_category(self, category):
        _logger.info('WooCommerce: export_category().')

        data = {'name': category['name']}

        if category['parent_id']:
            data['parent_id'] = category['parent_id']

        wc_category = self.create_obj(CATEGORIES, data=data)

        return wc_category['id']

    def export_inventory(self, inventory):
        _logger.info('WooCommerce: export_inventory()')

        upd_vals = defaultdict(list)
        result = list()
        id_to_code = dict()

        for external_code, inventory_data_list in inventory.items():
            ext_template_id, ext_variant_id = self._parse_product_external_code(external_code)

            endpoint = VARIATIONS % ext_template_id if ext_variant_id else PRODUCTS

            id_to_code[int(ext_variant_id or ext_template_id)] = external_code
            inventory_data = inventory_data_list[0]

            upd_vals[endpoint].append({
                'id': ext_variant_id or ext_template_id,
                'manage_stock': inventory_data['manage_stock'],
                'stock_quantity': inventory_data['stock_quantity'],
            })

        for endpoint, data in upd_vals.items():
            response = self.update_batch(endpoint, data)
            result.extend(
                [(id_to_code[int(x['id'])], not x.get('error'), '') for x in response]
            )

        return result

    @add_dynamic_kwargs
    def export_tracking(self, sale_order_id, tracking_data_list, **kw):
        _logger.info('WooCommerce: export_tracking()')

        tracking = ', '.join(set([x['tracking'] for x in tracking_data_list]))
        integration = self._get_integration(kw)
        tracking_field = integration.tracking_number_api_field_name

        if not tracking_field:
            return None

        order = self.fetch_one(ORDER % sale_order_id, params=self.prepare_lang_param())

        if not order:
            return None

        if tracking_field in order:
            data = {tracking_field: tracking}
        else:
            meta_data = list(filter(lambda x: x['key'] != tracking_field, order[META_DATA]))
            meta_data.append({
                'key': tracking_field,
                'value': tracking,
            })
            data = {META_DATA: meta_data}

        return self.update(ORDER % sale_order_id, data=data)

    def export_sale_order_status(self, vals):
        _logger.info('WooCommerce: export_sale_order_status()')

        return self.update(ORDER % vals['order_id'], data={'status': vals['status']})

    @add_dynamic_kwargs
    def get_product_for_import(self, product_code, import_images=False, **kw):
        _logger.info('WooCommerce: get_product_for_import()')
        # Get product
        env = self._get_env(kw)
        EcommerceField = env['product.ecommerce.field.mapping'].with_context(
            integration_id=self._integration_id,
        )
        template_fields = EcommerceField.get_translatable_template_api_names()

        template = self._get_template_with_translations(product_code, template_fields)
        if not template:
            raise UserError(
                _('Product with id "%s" does not exist in WooCommerce') % product_code
            )

        # Get combinations
        variant_fields = EcommerceField.get_translatable_variant_api_names()
        variants = self._get_variants_with_translations(product_code, variant_fields)

        images_hub = {
            'images': dict(),  # 'images': {'image_id': bin-data}
            'variants': dict(),  # variants: {'variant_id': [image-ids],}
        }

        for variant in variants:
            variant['template'] = template

        if import_images:
            image_urls = dict()  # {'image_id': image_url}
            for image in template['images']:
                image_urls[image['id']] = image['src']

            for variant in variants:
                variant_id = self._build_product_external_code(product_code, variant['id'])

                if variant.get('image'):
                    image_id = variant['image']['id']
                    images_hub['variants'][variant_id] = [image_id]
                    image_urls[image_id] = variant['image']['src']

            for image_id, image_url in image_urls.items():
                try:
                    images_hub['images'][image_id] = self._client.get_by_direct_link(image_url)
                except WooCommerceApiException:
                    pass

        return template, variants, list(), images_hub

    def _get_template_with_translations(self, template_external_id, fields):
        template = self.fetch_one(
            PRODUCT % template_external_id,
            params=self.prepare_lang_param(),
        )
        template_translated = self._receive_product_translations(template, fields)
        return template_translated

    def _get_variants_with_translations(self, template_external_id, fields):
        variants = self.fetch_list(
            VARIATIONS % template_external_id,
            params=self.prepare_lang_param(),
        )
        variant_list_translated = list()

        for variant in variants:
            variant_translated = self._receive_product_translations(variant, fields)
            variant_list_translated.append(variant_translated)

        return variant_list_translated

    def _receive_product_translations(self, external_product, field_list):
        product_lang = external_product.get('lang')
        translations_dict = external_product.get('translations')

        if not product_lang or not translations_dict or not field_list:
            return external_product

        product_data_list = [(product_lang, external_product)]
        for translation_code, external_id in translations_dict.items():
            if translation_code == product_lang:
                continue

            external_product_tr = self.fetch_one(
                PRODUCT % external_id,
                params=dict(lang=translation_code),
            )
            product_data_list.append((translation_code, external_product_tr))

        product_updated = deepcopy(external_product)
        meta_data_list = product_updated.pop(META_DATA, [])
        meta_data_dict = {x['key']: x['value'] for x in meta_data_list}
        product_updated[META_DATA] = list()

        for name in field_list:
            field_value_multi = list()

            for lang, external_data_tr in product_data_list:
                meta_data_dict_tr = {
                    x['key']: x['value'] for x in external_data_tr[META_DATA]
                }
                if self._is_metafield(name):
                    key = self._truncate_name_by_dot(name)
                    value = meta_data_dict_tr.pop(key, '')
                    meta_data_dict.pop(key, '')
                else:
                    value = external_data_tr.get(name)

                lang_value = {'attrs': {'id': lang}, 'value': value}
                field_value_multi.append(lang_value)

            field_value = dict(language=field_value_multi)

            if self._is_metafield(name):
                key = self._truncate_name_by_dot(name)
                product_updated[META_DATA].append(dict(key=key, value=field_value))
            else:
                product_updated[name] = field_value

        rest_of_meta = [dict(key=k, value=v) for k, v in meta_data_dict.items()]
        product_updated[META_DATA].extend(rest_of_meta)

        return product_updated

    @staticmethod
    def _is_metafield(field_name):
        return field_name.startswith(f'{META_DATA}.')

    @add_dynamic_kwargs
    def get_templates_and_products_for_validation_test(self, product_refs=None, **kw):
        _logger.info('WooCommerce: get_templates_and_products_for_validation_test()')

        integration = self._get_integration(kw)
        # Reference and barcode should have the same `name` for magento templates and variants
        barcode_field = integration._get_product_barcode_name()
        ecommerce_barcode = integration._template_field_name_to_ecommerce_name(barcode_field)

        def serialize_variant(v, parent_id):
            return {
                'id': v['id'],
                'name': v['name'],
                'barcode': v.get(ecommerce_barcode) or '',
                'ref': v.get('sku') or '',
                'parent_id': parent_id,
                'skip_ref': False,
                'joint_namespace': False,
            }

        def serialize_template(t, skip_ref):
            return {
                'id': t['id'],
                'name': t['name'],
                'barcode': t.get(ecommerce_barcode) or '',
                'ref': t.get('sku') or '',
                'parent_id': str(),
                'skip_ref': skip_ref,
                'joint_namespace': False,
            }

        product_filter = self._get_product_filter()
        # Get only fields required for validation
        product_filter['_fields'] = f'id,name,type,sku,{ecommerce_barcode}'
        products = self._get_products(product_filter)

        products_data = dict()

        for product in products:
            variants = list()
            product_id = product['id']

            if product['type'] == VARIABLE:
                variants = self.get(
                    VARIATIONS % product_id,
                    params={'_fields': f'id,sku,{ecommerce_barcode}'},
                )

            data = {product_id: [serialize_template(product, bool(variants))]}

            for variant in variants:
                variant['name'] = product['name']
                data[product_id].append(serialize_variant(variant, product_id))

            products_data.update(data)

        return TemplateHub(list(itertools.chain.from_iterable(products_data.values())))

    def get_stock_levels(self, *args, **kw):
        # For import inventory used get_stock_level_by_codes
        _logger.info('WooCommerce: get_stock_levels(). Not implemented.')
        return {}

    def get_stock_level_by_codes(self, template_ids, *args, **kw):
        product_filter = self._get_product_filter({'include': ','.join(template_ids)})
        templates = self._get_products(product_filter)

        stock_available = {}
        for template in templates:
            if template['type'] != VARIABLE or not template['variations']:
                if template['manage_stock']:
                    code = self._build_product_external_code(template['id'])
                    stock_available[code] = template['stock_quantity'] or 0
            else:
                for variant_id in template['variations']:
                    variant = self.fetch_one(VARIATION % (template['id'], variant_id))
                    if variant['manage_stock']:
                        code = self._build_product_external_code(template['id'], variant_id)
                        stock_available[code] = variant['stock_quantity'] or 0

        return stock_available

    def get_products_for_accessories(self):
        _logger.info('WooCommerce: get_products_for_accessories(). Not implemented.')
        return

    def create_webhooks_from_routes(self, routes_dict):
        _logger.info('WooCommerce: create_webhooks_from_routes()')
        result = dict()

        for name_tuple, route in routes_dict.items():
            data = {
                'name': name_tuple[1],
                'status': 'active',
                'topic': name_tuple[-1],
                'delivery_url': route,
            }

            webhook = self.create_obj(WEBHOOKS, data)

            result[name_tuple] = str(webhook['id'])

        return result

    def unlink_existing_webhooks(self, external_ids=None):
        _logger.info('WooCommerce: unlink_existing_webhooks()')
        result = self.delete_batch(WEBHOOKS, external_ids)
        return result

    def _get_url_pattern(self, wrap_li=True):
        pattern = f'<a href="{self.admin_url}/post.php?post=%s&action=edit" target="_blank">%s</a>'
        if wrap_li:
            return f'<li>{pattern}</li>'
        return pattern

    def _prepare_url_args(self, record):
        return ((record.parent_id or record.id), record.format_name)

    def _convert_to_html(self, id_list):
        pattern = self._get_url_pattern()
        arg_list = [self._prepare_url_args(x) for x in id_list]
        return ''.join([pattern % args for args in arg_list])

    @staticmethod
    def _convert_type_to_odoo(wc_template):
        if wc_template['type'] == SIMPLE and wc_template['virtual']:
            return 'service'
        return 'product'

    @staticmethod
    def _parse_product_external_code(code):
        """Redefined abstract method"""
        template_id, variant_id = code.split('-', 1)
        if variant_id == IS_FALSE:
            variant_id = False
        return template_id, variant_id

    # In WC attribute values saved in product by NAME, so we must parse it and find ID
    def parse_custom_attributes(self, product):
        result = []

        # Method only for variable templates and product variants (variants don't have "type")
        if product.get('type', 'variable') != 'variable':
            return result

        for attribute in product.get('attributes', []):
            if not attribute.get('variation', True):
                continue

            terms = self.get(ATTRIBUTE_VALUES % attribute['id'])

            if len(terms) != len(list(set([x['name'] for x in terms]))):
                raise UserError(
                    _('Product with id "%s" has attributes with same value names') % product['id']
                )

            for attribute_name in attribute.get('options', [attribute.get('option')]):
                attribute_value = list(filter(lambda x: x['name'] == attribute_name, terms))

                if len(attribute_value) != 1:
                    raise UserError(
                        _('Can''t find attribute value "%s" in attribute "%s"')
                        % (attribute_name, attribute['name'])
                    )

                result.append(attribute_value[0]['id'])

        return result

    @staticmethod
    def _parse_customer(customer):
        result = {
            'id': str(customer['id']),
            'person_name': ' '.join([customer['first_name'], customer['last_name']]),
            'email': customer['email'],
        }

        if customer.get('language'):
            result['language'] = customer['language']

        if not result['person_name'].strip():
            result['person_name'] = result['email']

        return result

    def _parse_address(self, customer, address, addr_type, vat_metafield=None, metadata=None):
        """
        we add customer id to address id to distinguish them from each other
        """

        if not address:
            return {}

        result = {
            'id': '',
            'person_name': ' '.join([address['first_name'], address['last_name']]),
            'email': address.get('email', customer.get('email')),
            'company_name': address['company'],
            'street': address['address_1'],
            'street2': address['address_2'],
            'city': address['city'],
            'country_code': address['country'],
            'state_code': address['state'],
            'zip': address['postcode'],
            'phone': address['phone'],
            'type': addr_type,
        }

        if not result['person_name'].strip():
            result['person_name'] = result['email']

        if vat_metafield and metadata:
            vat_number = self._get_meta_date_value(metadata, vat_metafield)
            if vat_number:
                result['company_reg_number'] = vat_number

        return result

    @staticmethod
    def _get_meta_date_value(metadata, metafield_name):
        value = list(filter(lambda x: x['key'] == metafield_name, metadata))
        return value and value[0]['value']

    def _get_fields_with_translations(self, endpoint, external_object, field_list):
        object_lang = external_object.get('lang')
        translations_dict = external_object.get('translations')

        if not object_lang or not translations_dict or not field_list:
            return external_object

        product_data_list = [(object_lang, external_object)]
        for translation_code, external_id in translations_dict.items():
            if translation_code == object_lang:
                continue

            external_object_tr = self.fetch_one(
                endpoint % external_id,
                params=dict(lang=translation_code),
            )
            product_data_list.append((translation_code, external_object_tr))

        result = dict()
        for name in field_list:
            field_value_multi = list()

            for lang, external_data_tr in product_data_list:
                value = external_data_tr.get(name)
                field_value_multi.append(
                    {'attrs': {'id': lang}, 'value': value},
                )

            field_value = dict(language=field_value_multi)
            result[name] = field_value

        return result
