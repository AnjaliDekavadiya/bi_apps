# See LICENSE file for full copyright and licensing details.

import copy
import logging
from collections import defaultdict
from itertools import chain
from datetime import timedelta
from urllib.parse import quote_plus

from odoo.addons.integration.tools import escape_trash, IS_FALSE
from odoo.addons.integration.api.abstract_apiclient import AbsApiClient
from odoo.addons.integration.tools import not_implemented, TemplateHub, add_dynamic_kwargs

from odoo import _
from odoo.tools import frozendict
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError, ValidationError

import requests

from .wizard.configuration_wizard_magento import ORDER_STATUS
from .magento2.client import Client
from .magento2.tools import MagentoOrder
from .magento2.exceptions import Magento2ApiException


_logger = logging.getLogger(__name__)


MAGENTO_TWO = 'magento2'

SIMPLE = 'simple'
VIRTUAL = 'virtual'
BUNDLE = 'bundle'
DOWNLOADABLE = 'downloadable'
GROUPED = 'grouped'
CONFIGURABLE = 'configurable'

PRODUCT_TYPES = {
    SIMPLE: 'product',
    VIRTUAL: 'service',
    BUNDLE: 'product',
    DOWNLOADABLE: 'service',
    GROUPED: 'product',
    CONFIGURABLE: 'product',
}

MAGENTO_FETCH_LIMIT = 1000
STATUS_ENABLED = 1
STATUS_DISABLED = 2

ALL_VIEWS = 'all'
DEFAULT_VIEW = 'default'
NON_TAX_CLASS = '1'
CUSTOM_ATTRIBUTES = 'custom_attributes'
EXTENSION_ATTRIBUTES = 'extension_attributes'


class Magento2ApiClient(AbsApiClient):

    settings_fields = (
        ('url', 'Shop URL', ''),
        ('admin_url', 'Admin URL', ''),
        ('key', 'Access Token', ''),
        ('receive_order_statuses', 'Order statuses separated by comma', 'pending'),
        ('default_attribute_set_id', 'Default attribute set', ''),
        ('default_attribute_group_id', 'Default attribute group', ''),
        ('default_product_category_id', 'Default product category', ''),
        ('default_location_id', 'Default Location', ''),
        ('shop_ids', 'Shop ids separated by comma (used all available if not specified)', ''),
        ('attribute_codes', 'Attribute codes separated by comma', '[]', True),
        ('import_products_filter', 'Import Products Filter', '[("status", "eq", 1)]', True),
        ('shop_weight_uoms', 'Magento 2 weight units. '
                             'Will be automatically populated when integration is active', '',),
        ('adapter_version', 'Version number of the api client', '0'),
        ('decimal_precision', 'Number of decimal places in the price of the exported product', '2'),
    )

    def __init__(self, settings):
        super().__init__(settings)
        self._client = self.get_client()
        self._shop_weight_uoms = self.get_settings_value('shop_weight_uoms')

    @property
    def admin_url(self):
        url = self.get_settings_value('admin_url')

        while url.endswith('/'):
            url = url[:-1]

        return url

    def build_headers(self):
        return self._client._build_headers()

    def get_client(self):
        host = self.get_settings_value('url')
        access_token = self.get_settings_value('key')
        shop_ids = self.get_settings_value('shop_ids')
        client = Client(host, access_token, shop_ids)
        return client

    def check_connection(self):
        self.stores_active()
        modules = self.fetch_multi('modules')
        return bool(modules)

    def get_api_resources(self):
        pass

    @property
    def store(self):
        return self._client._store()

    @property
    def lang(self):
        return self._client._lang()

    @property
    def store_weight_uom(self):
        return self._client.store_weight_uom

    def stores_all(self):
        return self._client._all_stores

    def stores_active(self):
        return self._client._stores_active()

    @add_dynamic_kwargs
    def store_view_codes(self, **kw):
        env = self._get_env(kw)
        language_mappings = env['integration.res.lang.mapping'].search([
            ('integration_id', '=', self._integration_id),
        ])
        lang_codes = language_mappings.mapped('external_language_id.code')

        store_view_codes = dict()
        if ALL_VIEWS in lang_codes:
            store_view_codes[ALL_VIEWS] = ALL_VIEWS

        for store in self.stores_active():
            store_view_code = store['code']
            locale = store['locale'].split('_')[0].lower()

            if locale in lang_codes:
                store_view_codes[store_view_code] = locale

        return store_view_codes

    @add_dynamic_kwargs
    def store_clients(self, foreign=False, **kw):
        store_view_codes = self.store_view_codes()(**kw)

        if foreign:
            lang_default = self.lang
            store_view_codes.pop(ALL_VIEWS, False)
            store_view_codes.pop(DEFAULT_VIEW, False)
            store_view_codes = {k: v for k, v in store_view_codes.items() if v != lang_default}

        clients = [self.with_store_view(k, v) for k, v in store_view_codes.items()]
        return clients

    def store_active_ids(self):
        return [str(x['id']) for x in self.stores_active()]

    def fetch_count(self, url, domain=None):
        kw = {
            'fields': 'items[id],total_count',
            'search_criteria[currentPage]': 1,
            'search_criteria[page_size]': MAGENTO_FETCH_LIMIT,
        }
        batch = self._client.get(url, domain=(domain or []), **kw)
        return batch['total_count']

    def fetch_one(self, url, record_id):
        return self._client._fetch_one(url, record_id)

    def fetch_multi(self, url, domain=None, fields=None, **kw):
        if fields:
            kw['fields'] = f'items[{",".join(fields)}]'

        batch = self._client.get(url, domain=domain, **kw)

        if isinstance(batch, dict) and 'items' in batch and not batch['items']:
            batch['items'] = list()

        return batch

    def fetch_multi_by_batch(self, url, domain=None, fields=None):
        result_list, count, page = [], 0, 1
        kw = {
            'search_criteria[currentPage]': page,
            'search_criteria[page_size]': MAGENTO_FETCH_LIMIT,
        }
        if fields:
            kw['fields'] = f'items[{",".join(fields)}],total_count'

        batch = self._client.get(url, domain=domain, **kw)

        items = batch.get('items', []) or []
        total_count = batch.get('total_count', 0)

        count += len(items)
        result_list.extend(items)

        while total_count > count:
            page += 1
            kw['search_criteria[currentPage]'] = page

            batch = self._client.get(url, domain=domain, **kw)

            items = batch.get('items', [])

            if not items:
                break

            count += len(items)
            result_list.extend(items)

        return result_list

    def fetch_multi_by_ids(self, url, ids, fields=None):
        """
        This method is used to fetch records by ids. We need to split ids into chunks to avoid
        exceeding the maximum url length.
        """
        products = []

        # Split ids list into chunks
        ids_chunks = [ids[i:i + 100] for i in range(0, len(ids), 100)]

        for ids_chunk in ids_chunks:
            # Make sure that ids are strings
            domain = [('entity_id', 'in', ','.join([str(x) for x in ids_chunk]))]

            batch = self.fetch_multi(url, domain=domain, fields=fields)
            products.extend(batch['items'])

        return products

    def save(self, url, data=None):
        return self._client.post(url, data=data)

    def apply(self, url, data=None):
        return self._client.put(url, data=data)

    def destroy(self, url):
        return self._client.delete(url)

    def with_store_view(self, store_view_code, locale=None):
        return self._client._with_store_view(store_view_code, locale)

    def get_order_class_parser(self):
        """Hook for external module extensions"""
        return MagentoOrder

    @add_dynamic_kwargs
    def get_delivery_methods(self, **kw):
        _logger.info('Magento: get_delivery_methods()')

        env = self._get_env(kw)
        integration = self._get_integration(kw)
        integration.integrationApiReceiveOrders()
        input_files = env['sale.integration.input.file'].search([
            ('si_id', '=', self._integration_id),
        ])

        # Parse delivery methods derectly from input-files
        carrier_set = set()
        for input_file in input_files:
            order = input_file.to_dict()
            ClassParser = self.get_order_class_parser()
            magento_order = ClassParser(self, order, env)
            shipping = magento_order.parse_shipping_formatted(to_tuple=True)
            if not shipping:
                continue
            carrier_set.add(shipping)

        return [dict(x) for x in carrier_set]

    def get_single_tax(self, tax_id):
        taxes = self.get_taxes()
        tax_list = [x for x in taxes if x['name'] == tax_id]
        return tax_list and tax_list[0] or dict()

    def get_taxes(self):
        _logger.info('Magento2: get_taxes()')
        tax_rates = self.fetch_multi('taxRates/search', domain=[], fields=['id', 'code', 'rate'])

        external_taxes = []
        for tax_rate in tax_rates['items']:
            external_tax = {
                'id': str(tax_rate['id']),
                'name': tax_rate['code'],
                'rate': tax_rate['rate'],
            }
            external_taxes.append(external_tax)

        # retrieve tax groups and convert to dictionary for fast searching
        tax_groups = self.fetch_multi('taxClasses/search', domain=[])
        tax_groups_dict = dict(
            (x['class_id'], x['class_name']) for x in tax_groups['items']
        )

        # retrieve all tax rules
        tax_rules = self.fetch_multi('taxRules/search', domain=[])

        # create dictionary of tax groups per tax
        tax_to_tax_rule_dict = defaultdict(set)
        for tax_rule in tax_rules['items']:
            tax_ids = tax_rule['tax_rate_ids']

            group_ids = tax_rule['product_tax_class_ids']  # Handle only `PRODUCT` taxes

            for tax_group_id in group_ids:
                tax_group_name = tax_groups_dict.get(tax_group_id)

                if not tax_group_name:
                    continue

                tax_group_dict = frozendict(
                    {
                        'id': str(tax_group_id),
                        'name': tax_group_name,
                    }
                )
                for tax_id in tax_ids:
                    tax_to_tax_rule_dict[str(tax_id)].add(tax_group_dict)

        for tax in external_taxes:
            tax['tax_groups'] = list(tax_to_tax_rule_dict.get(tax['id'], []))

        return external_taxes

    def get_countries(self):
        _logger.info('Magento2: get_countries()')
        countries = self.fetch_multi('directory/countries')

        external_countries = []
        for country in countries:
            external_country = {
                'id': str(country['id']),
                'name': country['full_name_english'],
                'external_reference': country['two_letter_abbreviation'],
            }
            external_countries.append(external_country)

        return external_countries

    def get_states(self):
        _logger.info('Magento2: get_states()')
        countries = self.fetch_multi('directory/countries')

        external_states = []
        for country in countries:
            country_code = country['two_letter_abbreviation']
            states = country.get('available_regions', [])

            for state in states:
                reference = self._build_state_external_code(
                    country_code, state['code'], state['id'],
                )
                external_state = {
                    'id': str(state['id']),
                    'name': state['name'],
                    'external_reference': reference,
                }
                external_states.append(external_state)

        return external_states

    def get_payment_methods(self):
        _logger.info('Magento: get_payment_methods(). Not implemented.')
        return list()

    def get_languages(self):
        _logger.info('Magento2: get_languages()')
        external_languages = set()

        external_languages.add(
            (
                ('id', ALL_VIEWS),
                ('name', 'All Store Views'),
                ('external_reference', 'all_ALL'),
            ),
        )

        for store_config in self.stores_all():
            lang = store_config['locale'].split('_')[0].lower()

            external_language = (
                ('id', lang),
                ('name', lang),
                ('external_reference', store_config['locale']),
            )
            external_languages.add(external_language)

        return [dict(lang) for lang in external_languages]

    def get_attributes(self):
        _logger.info('Magento2: get_attributes()')
        external_attributes = list()
        attributes = self._fetch_configurable_attributes()

        for attribute in attributes['items']:
            attribute_external_code = self._build_attribute_external_code(attribute)
            external_attribute = {
                'id': attribute_external_code,
                'name': attribute.get('default_frontend_label'),
            }
            external_attributes.append(external_attribute)

        return external_attributes

    def get_attribute_values(self):
        _logger.info('Magento2: get_attribute_values()')
        external_attribute_values = list()
        attributes = self._fetch_configurable_attributes()

        for attribute in attributes['items']:
            attribute_external_code = self._build_attribute_external_code(attribute)

            for option in attribute['options']:
                option_external_code = self._build_attribute_value_external_code(
                    attribute['attribute_id'],
                    option['value'],
                )

                if not option_external_code:
                    continue

                external_attribute_value = {
                    'id': option_external_code,
                    'name': option['label'],
                    'id_group': attribute_external_code,
                }
                external_attribute_values.append(external_attribute_value)

        return external_attribute_values

    def _attribute_value_check_existing(self, complex_id):
        attribute_id, option_value = self._parse_attribute_value_external_code(complex_id)
        response = self.fetch_multi(
            'products/attributes',
            domain=[('attribute_id', 'eq', attribute_id)],
        )
        if not response['items']:
            return False
        option_list = [x['value'] for x in response['items'][0]['options']]
        return option_value in option_list

    def get_features(self):
        _logger.info('Magento: get_features(). Not implemented.')
        return list()

    def get_feature_values(self):
        _logger.info('Magento: get_feature_values(). Not implemented.')
        return list()

    @add_dynamic_kwargs
    def get_locations(self, **kw):
        _logger.info('Magento: get_locations()')

        integration = self._get_integration(kw)
        if not integration.advanced_inventory():
            return list()

        locations = self.fetch_multi('inventory/sources', domain=[])

        def serialize(rec):
            return dict(id=rec['source_code'], name=rec['name'])

        return [serialize(x) for x in locations['items'] if x['enabled']]

    def get_pricelists(self):
        _logger.info('Magento: get_pricelists(). Not implemented.')
        return []

    def _fetch_attribute_ids_from_configurable_products(self):
        domain = [('type_id', 'eq', CONFIGURABLE)]
        settings_domain = self.get_settings_value('import_products_filter')
        domain.extend(settings_domain)
        field_list = ['id', EXTENSION_ATTRIBUTES]
        products = self.fetch_multi_by_batch('products', domain=domain, fields=field_list)

        attribute_ids = set()

        for product in products:
            attributes = self._parse_configurable_options(product)
            [attribute_ids.add(x['attribute_id']) for x in attributes]

        return attribute_ids

    def _fetch_configurable_attributes(self):
        attributes = dict(items=[])
        # TODO: Maybe we need to parse not the only configurable products
        attribute_ids = self._fetch_attribute_ids_from_configurable_products()

        attributes_from_settings = self.get_settings_value('attribute_codes')
        attribute_settings_ids = [x[0] for x in attributes_from_settings]
        attribute_ids.update(set(attribute_settings_ids))

        if attribute_ids:
            domain = [('attribute_id', 'in', ','.join(attribute_ids))]
            field_list = ['attribute_id', 'attribute_code', 'default_frontend_label', 'options']
            attributes = self.fetch_multi('products/attributes', domain=domain, fields=field_list)

        return attributes

    def get_categories(self):
        _logger.info('Magento2: get_categories()')

        field_list = ['id', 'name', 'parent_id']
        kw = {'search_criteria[pageSize]': 0}
        categories = self.fetch_multi('categories/list', domain=[], fields=field_list, **kw)

        external_categories = []
        for category in categories['items']:
            if 'name' not in category or 'id' not in category:
                continue

            external_category = {
                'id': str(category['id']),
                'name': category['name'],
                'id_parent': str(category['parent_id']),
            }
            external_categories.append(external_category)

        return external_categories

    def get_sale_order_statuses(self):
        _logger.info('Magento2: get_sale_order_statuses()')
        order_states = list()

        for state, values in ORDER_STATUS.items():
            order_states.append({
                'id': state,
                'name': values[0],
                'external_reference': False,
            })

        return order_states

    def get_product_template_ids(self):
        _logger.info('Magento2: get_product_template_ids()')

        templates = self.fetch_multi_by_batch(
            'products',
            domain=self._default_product_domain(),
            fields=['id', EXTENSION_ATTRIBUTES],
        )

        variant_ids = list()
        for template in templates:
            variant_ids.extend(
                self._parse_product_variants(template)
            )

        return [str(x['id']) for x in templates if x['id'] not in variant_ids]

    @add_dynamic_kwargs
    def get_product_templates(self, template_ids, **kw):
        _logger.info('Magento2: get_product_templates()')

        if not template_ids:
            return dict()

        integration = self._get_integration(kw)
        # Reference and barcode should have the same `name` for magento templates and variants
        barcode_field = integration._get_product_barcode_name()
        ecommerce_barcode = integration._template_field_name_to_ecommerce_name(barcode_field)

        field_list = [
            'id', 'name', 'sku', ecommerce_barcode, EXTENSION_ATTRIBUTES, CUSTOM_ATTRIBUTES,
        ]
        templates = self.fetch_multi_by_batch(
            'products',
            domain=[('entity_id', 'in', ','.join(template_ids))],
            fields=field_list,
        )

        all_attributes = self.fetch_multi_by_batch(
            'products/attributes',
            domain=[],
            fields=['attribute_id', 'attribute_code'],
        )
        attributes_router = {str(x['attribute_id']): x for x in all_attributes}

        # Pre-fetch variants for all templates
        variant_ids = []
        for template in templates:
            variant_ids.extend(self._parse_product_variants(template))

        if variant_ids:
            variants = self.fetch_multi_by_ids('products', ids=variant_ids, fields=field_list)

        result_list = list()

        for template in templates:
            template_attribute_codes = list()
            template_variants = list()
            variant_ids = self._parse_product_variants(template)

            if variant_ids:
                tmpl_attribute_ids, __ = self._parse_template_attributes(template)

                for attr_id in tmpl_attribute_ids:
                    attr = attributes_router[attr_id]
                    template_attribute_codes.append(
                        (attr['attribute_id'], attr['attribute_code'])
                    )
                template_variants = [x for x in variants if x['id'] in variant_ids]

            template_vals = {
                'id': str(template['id']),
                'name': template.get('name'),
                'barcode': self._parse_ecommerce_value(template, ecommerce_barcode) or None,
                'external_reference': template.get('sku') or None,
                'variants': list(),
            }

            for variant in template_variants:
                template_id = str(template['id'])

                attribute_value_ids = self._parse_attribute_values_by_codes(
                    template_attribute_codes,
                    self._parse_custom_attributes(variant),
                )
                template_vals['variants'].append({
                    'id': self._build_product_external_code(template_id, str(variant['id'])),
                    'name': variant.get('name'),
                    'barcode': self._parse_ecommerce_value(variant, ecommerce_barcode) or None,
                    'external_reference': variant.get('sku') or None,
                    'ext_product_template_id': template_id,
                    'attribute_value_ids': attribute_value_ids,
                })

            result_list.append(template_vals)

        return {x['id']: x for x in result_list}

    def get_customer_ids(self, date_since=None):
        _logger.info('Magento: get_customer_ids()')
        domain = list()
        if date_since:
            domain.append(('updated_at', 'gt', date_since - timedelta(days=1)))
        customers = self.fetch_multi_by_batch('customers/search', domain=domain, fields=['id'])
        return [x['id'] for x in customers]

    def get_customer_and_addresses(self, customer_id):
        _logger.info('Magento: get_customer_and_addresses()')
        customer = self.fetch_one('customers/search', customer_id)
        parsed_customer = self._parse_customer(customer)
        parsed_addreses = [self._parse_address(customer, x) for x in customer['addresses']]
        return parsed_customer, parsed_addreses

    def export_category(self, category):
        _logger.info('Magento2: export_category()')

        category_data = {
            'category': {
                'name': self._translate_if_need(category['name'], self.lang),
                'parent_id': category['parent_id'],
                'is_active': True,
            },
        }

        magento_category = self.save('categories', data=category_data)
        return str(magento_category['id'])

    def validate_template(self, template):
        _logger.info('Magento2: validate_template().')
        mappings_to_delete = []

        # (1) if template with such external id exists?
        magento_product_id = template['external_id']
        if magento_product_id:
            magento_product = self.fetch_one('products', magento_product_id)

            if not magento_product:
                mappings_to_delete.append({
                    'model': 'product.template',
                    'external_id': magento_product_id,
                })

        # (2) if part of the variants has no external_id?
        mappings_to_update = self.parse_mappings_to_update(template['products'])

        # (3) if variant with such external id exists?
        for variant in template['products']:
            variant_ext_id = variant['external_id']
            if not variant_ext_id:
                continue
            __, magento_combination_id = variant_ext_id.split('-')

            if magento_combination_id == IS_FALSE:
                magento_combination_id = None

            if magento_combination_id:
                magento_combination = self.fetch_one('products', magento_combination_id)

                if not magento_combination:
                    mappings_to_delete.append({
                        'model': 'product.product',
                        'external_id': variant_ext_id,
                    })

        return mappings_to_delete, mappings_to_update

    def find_existing_template(self, template):
        if template['external_id']:
            return False

        magento_type = self._get_magento_type(template)

        if magento_type == CONFIGURABLE:
            return self._find_configurable_template(template)
        return self._find_simple_template(template)

    def _find_configurable_template(self, template):
        prepared_variants = template['products']
        refs = [x['reference'] for x in prepared_variants]
        external_variant_list = self._find_product_by_references(refs)

        if not external_variant_list:
            # Find product with the same `sku` as were prepared in Odoo
            external_template_list = self._find_product_by_references(template['full_reference'])

            if external_template_list:
                external_template = external_template_list[0]
                template_combination_ids = self._parse_product_variants(external_template)

                raise UserError(
                    _(
                        'Amount of combinations in Magento is "%s". While amount in Odoo is "%s". '
                        'Please, check the product with id=%s (%s) in Magento and make sure it '
                        'has the same amount of combinations as variants in Odoo '
                        '(with enabled integration "%s").'
                    ) % (
                        len(template_combination_ids),
                        template['variant_count'],
                        external_template['id'],
                        external_template['type_id'],
                        self._integration_name,
                    )
                )

            return False

        if set(refs) != set(x['sku'] for x in external_variant_list):
            # TODO: here may be many cases. Some of the simple products there are in the shop..
            return False

        # Let's find the parent template
        products = self.fetch_multi('products', domain=[('type_id', 'eq', CONFIGURABLE)])['items']

        if not products:
            return False

        external_template_id = False
        combination_ids = [x['id'] for x in external_variant_list]

        for product in products:
            product_combination_ids = self._parse_product_variants(product)
            if set(combination_ids) == set(product_combination_ids):
                return external_template_id

        # TODO: here we have a case when the all variants were found in shop
        # but there is no parent template
        return external_template_id

    def _find_simple_template(self, template):
        ref = template['products'][0]['reference']
        external_template_list = self._find_product_by_references(ref)

        if not external_template_list:
            return False

        # Here may be many cases, for example external template have variants or kits or
        # belong other configurable product as a child
        return external_template_list[0]['id']

    def _find_product_by_references(self, product_refs):
        if product_refs and not isinstance(product_refs, list):
            product_refs = [str(product_refs)]

        domain = [('sku', 'in', ','.join(product_refs))]
        return self.fetch_multi('products', domain=domain)['items']

    @add_dynamic_kwargs
    def export_template(self, template, **kw):
        _logger.info('Magento2: export_template()')

        store_view_codes = self.store_view_codes()(**kw)

        if not store_view_codes:
            raise Exception('Magento2 Store Views not found.')

        result_mappings = list()
        for index, store_view_code in enumerate(store_view_codes, 1):
            _logger.info('Magento2: export template to store view "%s".', store_view_code)

            locale = store_view_codes[store_view_code]
            store_view_client = self.with_store_view(store_view_code, locale)
            mappings = self._export_template_to_store_view(template, store_view_client)(**kw)

            if index == 1:
                result_mappings.extend(mappings)

        return result_mappings

    @add_dynamic_kwargs
    def _export_template_to_store_view(self, template, store_view_client, **kw):
        """Create or update product."""
        template_external_id = template['external_id']
        magento_type = self._get_magento_type(template)

        if template_external_id:
            template_ = self.fetch_one('products', template_external_id)
            current_template_type = template_['type_id']

            if magento_type != current_template_type:
                raise Magento2ApiException(_(
                    'Product type in Odoo system (%s) not match current product type in Magento 2 '
                    '(%s). So what you need to do is: (1) Archive old products on Magento 2; '
                    '(2) Delete this product from "External -> Products" (find their product with '
                    'code "%s" and deleted it); (3) Then force the export product to Magento 2 '
                    'again (by clicking "Force Export to External" on the Product Template in the '
                    '"Action" dropdown. As result, a new Configurable Product will be created '
                    'in Magento 2.'
                ) % (magento_type, template_external_id, current_template_type))

        if magento_type == BUNDLE:
            bundle_mappings = self._export_bundle(
                template,
                store_view_client,
            )
            return bundle_mappings

        if magento_type == VIRTUAL:
            virtual_mappings = self._export_virtual(
                template,
                store_view_client,
            )
            return virtual_mappings

        if magento_type == SIMPLE:
            variant = copy.deepcopy(template['products'][0])
            variant['fields'] = dict()

            simple_mapping, __ = self._export_simple(
                template,
                variant,
                store_view_client,
            )
            return simple_mapping

        #  Removes inactive internal variant-associated external variants from a template.
        if template_external_id:
            # Obtain the list of external variant IDs associated with the template.
            ext_variant_ids = self._parse_product_variants(template_)
            # Obtain the list of internal variant IDs associated with the template.
            odoo_variant_ids = [
                int(self._parse_attribute_external_code(rec['external_id'])[1])
                for rec in template['products'] if rec.get('external_id')
            ]
            # If the two lists of variant IDs don't match, remove the missing ones.
            if set(ext_variant_ids) != set(odoo_variant_ids):
                missing_ids = set(ext_variant_ids) - set(odoo_variant_ids)
                for rec_id in missing_ids:
                    self._remove_variant(rec_id)

        mappings = list()
        template_external_id = None
        export_configurable = magento_type == CONFIGURABLE

        if export_configurable:
            # Here is three step export.
            # 1. export parent
            template_mapping = self._export_configurable(template, store_view_client)
            mappings.append(template_mapping)

            template_external_id = template_mapping['external_id']

        simple_ids = list()
        for variant in template['products']:
            # 2. configurable-childs
            simple_mappings, magento_product_id = self._export_simple(
                template,
                variant,
                store_view_client,
                parent_external=template_external_id,
            )
            mappings.extend(simple_mappings)
            simple_ids.append(magento_product_id)

        if export_configurable:
            # 3. assign childs to configurable
            self._assign_simple_to_configurable(template, store_view_client, simple_ids)(**kw)

        return mappings

    def _remove_variant(self, product_id):
        _logger.info('Magento 2: _remove_variant()')

        variant_ = self.fetch_one('products', product_id)
        sku = quote_plus(variant_['sku'])
        return self.destroy(f'products/{sku}')

    def _export_bundle(self, template, store_view_client):
        _logger.info('Magento2: _export_bundle()')
        assert len(template['kits']) == 1

        kit = template['kits'][0]
        variant = template['products'][0]
        template_external_id = template['external_id']

        bundle_product_options = list()
        for index, component in enumerate(kit['components'], start=1):
            __, component_id = self._parse_product_external_code(component['product_id'])
            product_ = self.fetch_one('products', component_id)
            sku = quote_plus(product_['sku'])

            product_link = {
                'id': component_id,
                'sku': sku,
                'qty': component['qty'],
                'position': index,
            }
            if index == 1:
                product_link['is_default'] = True

            bundle_product_option = {
                'title': component['name'],
                'type': 'radio',
                'product_links': [product_link],
                'required': True,
            }
            bundle_product_options.append(bundle_product_option)

        custom_attributes = [{
            'attribute_code': 'price_view',
            'value': 0,
        }]

        if not template_external_id:
            custom_attributes.append({
                'attribute_code': 'url_key',
                'value': self._generate_url_key(template['name'], template['id']),
            })

        specific_data = {
            'type_id': BUNDLE,
            EXTENSION_ATTRIBUTES: {
                'bundle_product_options': bundle_product_options,
            },
            CUSTOM_ATTRIBUTES: custom_attributes,
        }
        data = self._prepare_product_data(template, variant, store_view_client, specific_data)

        magento_product = self._create_or_update_product(
            store_view_client,
            template_external_id,
            data,
        )

        magento_product_id = str(magento_product['id'])
        mappings = [
            {
                'id': template['id'],
                'model': 'product.template',
                'external_id': magento_product_id,
            },
            {
                'id': variant['id'],
                'model': 'product.product',
                'external_reference': magento_product['sku'],
                'external_id': self._build_product_external_code(magento_product_id),
            },
        ]

        if not template_external_id:
            template['external_id'] = magento_product_id

        return mappings

    def _export_virtual(self, template, store_view_client):
        _logger.info('Magento2: _export_virtual()')

        specific_data = {
            'type_id': VIRTUAL,
            CUSTOM_ATTRIBUTES: list(),
        }
        variant = template['products'][0]
        template_external_id = template['external_id']

        if not template_external_id:
            specific_data[CUSTOM_ATTRIBUTES].append({
                'attribute_code': 'url_key',
                'value': self._generate_url_key(template['name'], template['id'], variant['id']),
            })

        data = self._prepare_product_data(template, variant, store_view_client, specific_data)
        magento_product = self._create_or_update_product(
            store_view_client,
            template_external_id,
            data,
        )

        magento_product_id = str(magento_product['id'])
        variant_external_id = self._build_product_external_code(magento_product_id)

        mappings = [
            {
                'id': template['id'],
                'model': 'product.template',
                'external_id': magento_product_id,
            },
            {
                'id': variant['id'],
                'model': 'product.product',
                'external_id': variant_external_id,
                'external_reference': magento_product['sku'],
            },
        ]

        if not template_external_id:
            template['external_id'] = magento_product_id
            variant['external_id'] = variant_external_id

        return mappings

    def _export_configurable(self, template, store_view_client):
        _logger.info('Magento2: _export_configurable()')

        specific_data = {
            'type_id': CONFIGURABLE,
            CUSTOM_ATTRIBUTES: list(),
        }
        template_id = template['id']
        template_external_id = template['external_id']

        if not template_external_id:
            specific_data['sku'] = template['full_reference']

            specific_data[CUSTOM_ATTRIBUTES].append({
                'attribute_code': 'url_key',
                'value': self._generate_url_key(template['name'], template['id']),
            })

        variant = dict(external_id=template_external_id)
        data = self._prepare_product_data(template, variant, store_view_client, specific_data)

        magento_product = self._create_or_update_product(
            store_view_client,
            template_external_id,
            data,
        )

        magento_product_id = str(magento_product['id'])
        mapping = {
            'id': template_id,
            'model': 'product.template',
            'external_id': magento_product_id,
            'external_reference': magento_product['sku'],
        }

        if not template_external_id:
            template['external_id'] = magento_product_id

        return mapping

    def _export_simple(self, template, variant, store_view_client, parent_external=False):
        _logger.info('Magento2: _export_simple()')

        specific_data = {
            'type_id': SIMPLE,
            CUSTOM_ATTRIBUTES: list(),
        }
        variant_external_id = variant['external_id']

        if not variant_external_id:
            # If there is no `fields` - it's just a simple template (with one variant)
            variant_id = variant['id'] if variant['fields'] else False

            specific_data[CUSTOM_ATTRIBUTES].append({
                'attribute_code': 'url_key',
                'value': self._generate_url_key(template['name'], template['id'], variant_id),
            })

        custom_attributes = list()
        for attribute_value in variant['attribute_values']:
            __, attribute_code = self._parse_attribute_external_code(
                attribute_value['attribute'],
            )
            __, value = self._parse_attribute_value_external_code(
                attribute_value['external_id'],
            )
            custom_attribute = {
                'attribute_code': attribute_code,
                'value': value,
            }
            custom_attributes.append(custom_attribute)

        specific_data[CUSTOM_ATTRIBUTES].extend(custom_attributes)

        if variant_external_id:
            __, variant_external_id = self._parse_product_external_code(variant_external_id)
            specific_data['id'] = variant_external_id

        data = self._prepare_product_data(template, variant, store_view_client, specific_data)

        magento_product = self._create_or_update_product(
            store_view_client,
            variant_external_id,
            data,
        )

        if template['type'] == 'consu':
            self._disable_manage_stock(magento_product)

        mappings = list()
        magento_product_id = str(magento_product['id'])

        if parent_external:
            external_id = self._build_product_external_code(parent_external, magento_product_id)
        else:
            external_id = self._build_product_external_code(magento_product_id)

            template_mapping = {
                'id': template['id'],
                'model': 'product.template',
                'external_id': magento_product_id,
            }
            mappings.append(template_mapping)

        variant_mapping = {
            'id': variant['id'],
            'model': 'product.product',
            'external_id': external_id,
            'external_reference': magento_product['sku'],
        }
        mappings.append(variant_mapping)

        if not variant_external_id:
            variant['external_id'] = external_id

        return mappings, magento_product_id

    @add_dynamic_kwargs
    def _assign_simple_to_configurable(self, template, store_view_client, simple_ids, **kw):
        _logger.info('Magento2: _assign_simple_to_configurable()')

        attributes = defaultdict(set)
        for product in template['products']:
            for attribute_value in product['attribute_values']:
                attribute_external_code = attribute_value['attribute']
                __, value = self._parse_attribute_value_external_code(
                    attribute_value['external_id'],
                )
                attributes[attribute_external_code].add(value)

        configurable_product_options = list()
        env = self._get_env(kw)
        AttributeExternal = env['integration.product.attribute.external']

        for attribute_external_code, values in attributes.items():
            magento_values = [{'value_index': x} for x in values]

            attribute = AttributeExternal.search([
                ('code', '=', attribute_external_code),
                ('integration_id', '=', self._integration_id),
            ])
            attribute_id, __ = self._parse_attribute_external_code(attribute_external_code)

            product_option = {
                'attribute_id': attribute_id,
                'label': attribute.name,
                'values': magento_values,
            }
            configurable_product_options.append(product_option)

        specific_data = {
            EXTENSION_ATTRIBUTES: {
                'configurable_product_options': configurable_product_options,
                'configurable_product_links': simple_ids,
            },
        }
        external_id = template['external_id']
        variant = dict(external_id=external_id)

        data = self._prepare_product_data(template, variant, store_view_client, specific_data)
        self._create_or_update_product(store_view_client, external_id, data)

        return True

    def _prepare_product_data(self, template, variant, store_view_client, specific_data):
        product_data = {
            'product': {
                'visibility': 4,
                'type_id': SIMPLE,
            },
            'save_options': 1,
        }
        if variant.get('external_id'):
            __, variant_external_id = self._parse_product_external_code(variant['external_id'])
            result = store_view_client._fetch_one('products', variant_external_id)
            product_data['product'].update(result)

        lang = store_view_client._lang()
        template_values = copy.deepcopy(template['fields'])
        variant_values = variant.get('fields', {})
        extension_attributes = dict()

        if CUSTOM_ATTRIBUTES not in template_values:
            template_values[CUSTOM_ATTRIBUTES] = list()

        if variant_values:
            template_values[CUSTOM_ATTRIBUTES].extend(variant_values.pop(CUSTOM_ATTRIBUTES, []))
            template_values.update(variant_values)

        for field, value in template_values.items():
            if field == CUSTOM_ATTRIBUTES:
                value = [
                    {
                        'attribute_code': attribute['attribute_code'],
                        'value': self._translate_if_need(attribute['value'], lang)
                    } for attribute in value
                ]

            product_data['product'][field] = self._translate_if_need(value, lang)

        # merge custom attributes
        product_data['product'][CUSTOM_ATTRIBUTES].extend(
            specific_data.pop(CUSTOM_ATTRIBUTES, []))

        if not variant.get('external_id'):
            attribute_set_id = self.get_required_settings_value('default_attribute_set_id')
            product_data['product']['attribute_set_id'] = int(attribute_set_id)

        # merge extension attributes
        specific_extension_attributes = specific_data.pop(EXTENSION_ATTRIBUTES, {})
        product_data['product'].update(specific_data)
        extension_attributes.update(specific_extension_attributes)

        product_data['product'][EXTENSION_ATTRIBUTES] = extension_attributes

        # Find weight for store. We use it, because in different stores can be different
        # units of weight measure
        weight = product_data['product'].get('weight')
        if weight and isinstance(weight, dict):
            store_weight = weight.get(store_view_client.store_view_code, 0)
            product_data['product']['weight'] = store_weight

        return product_data

    @staticmethod
    def _translate_if_need(value, lang):
        if isinstance(value, dict) and value.get('language'):
            return value['language'][lang]
        else:
            return value

    @add_dynamic_kwargs
    def export_images(self, images, **kw):
        _logger.info('Magento2: export_images()')
        results = list()
        template_images_data = images['template']

        if len(images['products']) > 1:
            res = self._export_images(template_images_data)(**kw)
            results.extend(res)

        for product_images_data in images['products']:
            if not product_images_data['default']:
                product_images_data['default'] = template_images_data['default']

            product_images_data['extra'] = (
                template_images_data['extra'] + product_images_data['extra']
            )
            res = self._export_images(product_images_data)(**kw)
            results.extend(res)

        return results

    @add_dynamic_kwargs
    def _export_images(self, images_data, **kw):
        external_id = images_data['id']
        images, media_gallery_entries = [], []
        clients = self.store_clients()(**kw)

        data = {
            'product': {
                'sku': images_data['default_code'],
                'media_gallery_entries': media_gallery_entries,
            },
        }

        # 1. Drop old images
        for client in clients:
            self._create_or_update_product(client, external_id, data)

        # 2. Collect bin-data
        default_image = images_data['default']
        if default_image:
            images.append(default_image)

        images.extend(images_data['extra'])

        for position, image in enumerate(images, 1):
            name = f'Image {position}'
            bin_data = image['data']

            media_gallery_entry = {
                'media_type': 'image',
                'label': name,
                'position': position,
                'disabled': False,
                'types': [],
                'content': {
                    'base64_encoded_data': bin_data.decode('ascii'),
                    'type': image['mimetype'],
                    'name': name,
                },
            }

            if default_image and position == 1:
                media_gallery_entry['types'].extend(['thumbnail', 'image', 'small_image'])

            media_gallery_entries.append(media_gallery_entry)

        # 3. Send new images
        results = list()
        for index, client in enumerate(clients, 1):
            store_code = client.store_view_code
            result = self._create_or_update_product(client, external_id, data)
            image_ids = [
                x['id'] for x in result['media_gallery_entries'] if x['media_type'] == 'image'
            ]
            results.append((store_code, external_id, image_ids))
            if index == 1:
                data['product']['media_gallery_entries'] = result['media_gallery_entries']

        return results

    def export_attribute(self, attribute):
        _logger.info('Magento2: export_attribute()')
        attribute_id = attribute['id']
        attribute_code = f'odoo_{attribute_id}'
        attribute_data = {
            'attribute': {
                'frontend_input': 'select',
                'attribute_code': attribute_code,
                'default_frontend_label': self._translate_if_need(attribute['name'], self.lang),
            },
        }

        magento_attribute = self.save(
            'products/attributes',
            attribute_data,
        )

        attribute_set_id = int(
            self.get_required_settings_value('default_attribute_set_id'),
        )
        attribute_group_id = int(
            self.get_required_settings_value('default_attribute_group_id'),
        )
        attach_attribute_data = {
            'attribute_set_id': attribute_set_id,
            'attribute_group_id': attribute_group_id,
            'attribute_code': attribute_code,
            'sort_order': 0,
        }
        self.save(
            'products/attribute-sets/attributes',
            attach_attribute_data,
        )

        external_code = self._build_attribute_external_code(magento_attribute)

        return external_code

    def export_attribute_value(self, attribute_value):
        _logger.info('Magento2: export_attribute_value()')
        __, attribute_code = self._parse_attribute_external_code(
            attribute_value['attribute'],
        )
        option_data = {
            'option': {
                'label': self._translate_if_need(attribute_value['name'], self.lang),
            },
        }
        magento_option_value = self.save(
            f'products/attributes/{attribute_code}/options',
            option_data,
        )
        external_code = self._build_attribute_value_external_code(
            attribute_code,
            magento_option_value,
        )
        return external_code

    @not_implemented
    def export_feature(self, feature):
        pass

    @not_implemented
    def export_feature_value(self, feature_value):
        pass

    @add_dynamic_kwargs
    def export_inventory(self, inventory, **kw):
        _logger.info('Magento2: export_inventory()')

        integration = self._get_integration(kw)
        if integration.advanced_inventory():
            result = self._export_ms_inventory(inventory)
        else:
            result = self._export_inventory(inventory)

        return result

    def _export_inventory(self, inventory):
        _logger.info('Magento2: export standard inventory')

        results = list()
        for external_code, inventory_data_list in inventory.items():
            __, variant_id = self._parse_product_external_code(external_code)
            product = self.fetch_one('products', variant_id)
            if not product:
                message = _('External product "%s" does not exist.') % variant_id
                results.append((external_code, False, message))
                continue

            sku = product.get('sku')
            if not sku:
                message = _(
                    'Product "%s" has no requred property "stock keeping unit".' % variant_id
                )
                results.append((external_code, False, message))
                continue

            sku = quote_plus(sku)
            stock_items = self._client.get(f'stockItems/{sku}')

            inventory_data = inventory_data_list[0]
            qty = inventory_data['qty']
            stock_item_id = stock_items['item_id']

            stock_item_update_data = {
                'stock_item': {
                    'qty': qty,
                    'is_in_stock': qty > 0,
                }
            }
            res = self.apply(
                f'products/{sku}/stockItems/{stock_item_id}',
                stock_item_update_data,
            )
            results.append((external_code, res, ''))

        return results

    def _export_ms_inventory(self, inventory):
        _logger.info('Magento2: export multi-source inventory')
        default_location_id = self.get_settings_value('default_location_id')

        results, data_list = list(), list()
        for external_code, inventory_data_list in inventory.items():
            __, variant_id = self._parse_product_external_code(external_code)
            product = self.fetch_one('products', variant_id)
            if not product:
                message = _('External product "%s" does not exist.') % variant_id
                results.append((external_code, False, message))
                continue

            sku = product.get('sku')
            if not sku:
                message = _(
                    'Product "%s" has no requred property "stock keeping unit".' % variant_id
                )
                results.append((external_code, False, message))
                continue

            for inventory_data in inventory_data_list:
                location_id = inventory_data['external_location_id'] or default_location_id
                qty = int(inventory_data['qty'])

                data = dict(
                    sku=sku,
                    quantity=qty,
                    status=int(qty > 0),
                    source_code=location_id,
                )
                data_list.append(data)
                results.append((external_code, True, ''))
        # TODO: the `save` method returns empty list, so we can only return True in results
        self.save('inventory/source-items', {'sourceItems': data_list})
        return results

    @add_dynamic_kwargs
    def order_fetch_kwargs(self, **kw):
        integration = self._get_integration(kw)
        order_statuses = self.get_settings_value('receive_order_statuses')
        cut_off_datetime = integration.orders_cut_off_datetime_str

        domain = [
            ('status', 'in', order_statuses),
            ('store_id', 'in', ','.join(self.store_active_ids())),
            ('updated_at', 'gt', integration.last_receive_orders_datetime_str),
        ]

        if cut_off_datetime:
            domain.append(('created_at', 'gt', cut_off_datetime))

        return {
            'domain': domain,
            'search_criteria[currentPage]': 1,
            'search_criteria[sortOrders][0][field]': 'updated_at',
            'search_criteria[sortOrders][0][direction]': 'ASC',
            'search_criteria[page_size]': self.order_limit_value(),

        }

    @add_dynamic_kwargs
    def receive_orders(self, **kw):
        _logger.info('Magento2: receive_orders()')

        kwargs = self.order_fetch_kwargs()(**kw)
        orders_data = self.fetch_multi('orders', **kwargs)
        orders = orders_data['items']

        result = list()
        for order in orders:
            vals = dict(
                id=str(order['entity_id']),
                data=order,
                updated_at=order['updated_at'],
                created_at=order['created_at'],
            )
            result.append(vals)

        return result

    def receive_order(self, order_id):
        input_file = dict()
        order = self.fetch_one('orders', order_id)
        if not order:
            return input_file

        input_file['id'] = order_id
        input_file['data'] = order
        return input_file

    @add_dynamic_kwargs
    def parse_order(self, input_file, **kw):
        env = self._get_env(kw)
        ClassParser = self.get_order_class_parser()
        magento_order = ClassParser(self, input_file, env)
        result = magento_order.parse()
        return result

    def export_tracking(self, sale_order_id, tracking_data_list):
        _logger.info('Magento2: export_tracking()')

        ship_data = self._collect_shipping_data(tracking_data_list)

        result = self.save(
            f'order/{sale_order_id}/ship',
            ship_data,
        )
        return result

    @staticmethod
    def _collect_shipping_data(tracking_data_list):
        items = set()
        tracks = list()

        for tracking_data in tracking_data_list:
            for line in tracking_data['lines']:
                item = (
                    ('qty', line['qty']),
                    ('order_item_id', line['id']),
                )
                items.add(item)

            if tracking_data['tracking']:
                track = {
                    'title': tracking_data['name'],
                    'track_number': tracking_data['tracking'],
                    'carrier_code': tracking_data['carrier'],
                }
                tracks.append(track)

        ship_data = {
            'notify': True,
            'items': [dict(x) for x in items],
        }

        if tracks:
            ship_data['tracks'] = tracks

        return ship_data

    def export_sale_order_status(self, vals):
        method_name = f'_export_sub_status_{vals["status"]}'

        if hasattr(self, method_name):
            return getattr(self, method_name)(vals)

        raise NotImplementedError(f'Magento2 method "{method_name}" is still not implemented.')

    def _export_sub_status_processing(self, vals):
        order_id = vals['order_id']
        order = self.fetch_one('orders', order_id)

        total_invoiced = order.get('total_invoiced')
        if total_invoiced and total_invoiced == order['grand_total']:
            return _('Order %s was already fully invoiced in Magento') % order_id

        url = f'order/{order_id}/invoice'
        data = dict(capture=True, notify=True)
        res = self.save(url, data)
        return res

    def _fetch_image_bin_data(self, file_url):
        store_url = self.store['base_media_url']
        image_url = f'{store_url}/catalog/product{file_url}'

        response = requests.get(image_url, headers=self.build_headers())
        if response.ok:
            return response.content
        return False

    @add_dynamic_kwargs
    def get_product_for_import(self, product_code, import_images=False, **kw):
        _logger.info('Magento2: get_product_for_import()')

        product = self.fetch_one('products', product_code)
        if not product:
            raise UserError(
                _('Product with id "%s" does not exist in Magento 2.') % product_code
            )

        product_type = product['type_id']
        assert product_type in (SIMPLE, CONFIGURABLE, VIRTUAL, DOWNLOADABLE)

        clients = self.store_clients(foreign=True)(**kw)
        lang_versions = {
            x._lang(): x._fetch_one('products', product_code) for x in clients
        }
        tmpl_attribute_ids, tmpl_attribute_value_ids = self._parse_template_attributes(product)
        custom_attributes = self._parse_custom_attributes(product)

        template = {
            'product': product,
            'tmpl_attribute_value_ids': tmpl_attribute_value_ids,
            CUSTOM_ATTRIBUTES: custom_attributes,
            'lang_versions': lang_versions,
        }
        images_hub = {
            'images': dict(),  # 'images': {'image_id': bin-data,}
            'variants': dict(),  # variants: {'variant_id': [image-ids],}
        }
        # Parse template images
        if import_images:
            image_list = self._parse_product_images(product)

            for image in image_list:
                bin_data = self._fetch_image_bin_data(image['file'])

                if bin_data:
                    image_id = str(image['id'])
                    images_hub['images'][image_id] = bin_data

        variants = list()
        bom_components = list()

        if product_type != CONFIGURABLE:
            return template, variants, bom_components, images_hub

        attribute_codes = list()
        product_variant_ids = self._parse_product_variants(product)

        if tmpl_attribute_ids:
            domain = [('attribute_id', 'in', ','.join(tmpl_attribute_ids))]
            attributes = self.fetch_multi('products/attributes', domain=domain)
            attribute_codes = [
                (x['attribute_id'], x['attribute_code']) for x in attributes['items']
            ]

        for variant_id in map(str, product_variant_ids):
            variant = self.fetch_one('products', variant_id)
            custom_attributes = self._parse_custom_attributes(variant)
            variants.append({
                'product_attribute_codes': attribute_codes,
                'variant': variant,
                'product_code': product_code,
                CUSTOM_ATTRIBUTES: custom_attributes,
            })
            # Parse variant images
            if import_images:
                variant_list = list()
                image_list = self._parse_product_images(variant)

                for image in image_list:
                    bin_data = self._fetch_image_bin_data(image['file'])

                    if bin_data:
                        image_id = str(image['id'])

                        variant_list.append(image_id)
                        images_hub['images'][image_id] = bin_data

                images_hub['variants'][variant_id] = variant_list

        return template, variants, bom_components, images_hub

    @not_implemented
    def get_stock_levels(self, *args, **kw):
        pass

    @add_dynamic_kwargs
    def get_stock_levels_one(self, product_id, external_code, **kw):
        _logger.info('Magento2: get_stock_levels_one(%s, %s)', product_id, external_code)

        integration = self._get_integration(kw)
        if integration.advanced_inventory():
            result = self._get_stock_levels_one_ms(product_id, external_code)
        else:
            result = self._get_stock_levels_one(product_id)

        return result

    def _get_stock_levels_one_ms(self, product_id, external_code):
        _logger.info('Magento2: get stock levels MS')

        external_product = self.fetch_one('products', product_id)
        if not external_product:
            return False
        sku = quote_plus(external_product['sku'])

        items = self.fetch_multi('inventory/source-items', domain=[('sku', 'eq', sku)])['items']

        source_code = external_code or self.get_settings_value('default_location_id')
        if source_code:
            quantity = sum(x['quantity'] for x in items if x['source_code'] == source_code)
        else:
            quantity = int()

        return {'qty': quantity}

    def _get_stock_levels_one(self, product_id):
        _logger.info('Magento2: get stock levels standard')
        external_product = self.fetch_one('products', product_id)

        sku = quote_plus(external_product['sku'])
        result = self._client.get(f'stockItems/{sku}')
        return result

    @not_implemented
    def get_products_for_accessories(self):
        pass

    @add_dynamic_kwargs
    def get_templates_and_products_for_validation_test(self, product_refs=None, **kw):
        _logger.info('Magento2: get_templates_and_products_for_validation_test()')

        integration = self._get_integration(kw)
        # Reference and barcode should have the same `name` for magento templates and variants
        barcode_field = integration._get_product_barcode_name()
        ecommerce_barcode = integration._template_field_name_to_ecommerce_name(barcode_field)

        domain = self._default_product_domain()

        if product_refs and not isinstance(product_refs, list):
            product_refs = [str(product_refs)]

        if product_refs:
            domain.append(('sku', 'in', ','.join(product_refs)))

        products = self.fetch_multi_by_batch(
            'products',
            domain=domain,
            fields=[
                'id', 'name', 'sku', ecommerce_barcode, EXTENSION_ATTRIBUTES, CUSTOM_ATTRIBUTES,
            ],
        )

        variant_ids = set()
        products_dict = dict()
        products_data = defaultdict(list)

        # 1. Parse Variant IDS
        for product in products:
            products_dict[product['id']] = product

            variant_ids.update(
                self._parse_product_variants(product)
            )

        # 2. Serialize templates
        for product in products:
            product_id = product['id']

            if product_id not in variant_ids:
                products_data[product_id].append({
                    'id': str(product_id),
                    'name': product.get('name'),
                    'barcode': self._parse_ecommerce_value(product, ecommerce_barcode) or '',
                    'ref': product.get('sku') or '',
                    'parent_id': '',
                    'skip_ref': False,
                    'joint_namespace': True,
                })

        # 3.1. Fetch missed variants before serialization to avoid a lot of fetch_one requests
        # For some reason, we fetch only enabled products BUT at the same time we fetch
        # disabled variants! This can lead to a large number of requests to the API.
        missed_variant_ids = list()
        for product in products:
            for variant_id in self._parse_product_variants(product):
                if not products_dict.get(variant_id):
                    missed_variant_ids.append(variant_id)

        # Fetch missed variants
        if missed_variant_ids:
            missed_variants = self.fetch_multi_by_ids('products', ids=missed_variant_ids)
            missed_variants_dict = {v['id']: v for v in missed_variants}

        # 3.2. Serialize variants
        for product in products:
            product_id = product['id']

            for variant_id in self._parse_product_variants(product):
                variant = products_dict.get(variant_id) or missed_variants_dict.get(variant_id)

                if not variant:
                    variant = self.fetch_one('products', variant_id)

                    if not variant:
                        raise ValidationError(_(
                            'External product variant not found: %s-%s' % (product_id, variant_id)
                        ))
                    if variant['type_id'] not in (SIMPLE, VIRTUAL, DOWNLOADABLE):
                        raise ValidationError(_(
                            'Product variant %s-%s belong to the "%s" type.'
                        ) % (product_id, variant_id, variant['type_id']))

                products_data[product_id].append({
                    'id': str(variant_id),
                    'name': variant.get('name'),
                    'barcode': self._parse_ecommerce_value(variant, ecommerce_barcode) or '',
                    'ref': variant.get('sku') or '',
                    'parent_id': str(product_id),
                    'skip_ref': False,
                    'joint_namespace': True,
                })

        # If there is at least one variant, template reference is not essential.
        for product_list in products_data.values():
            if len(product_list) > 1:
                for tmpl_dict in filter(lambda x: not x['parent_id'], product_list):
                    tmpl_dict['skip_ref'] = True

        return TemplateHub(list(chain.from_iterable(products_data.values())))

    def _parse_attribute_values_by_codes(self, attribute_codes, custom_attributes):
        attribute_value_ids = list()
        for attr_id, attr_code in attribute_codes:
            attribute_value_id = self._build_attribute_value_external_code(
                attr_id,
                custom_attributes.get(attr_code),
            )
            if not attribute_value_id:
                continue
            attribute_value_ids.append(attribute_value_id)

        return attribute_value_ids

    def _parse_template_attributes(self, product):
        attribute_ids = list()
        attribute_value_ids = list()

        # 1. Parse configurable attributes
        configurable_options = self._parse_configurable_options(product)
        for option in configurable_options:
            attribute_id = option['attribute_id']
            attribute_ids.append(attribute_id)

            for value in option.get('values', []):
                attribute_value_id = self._build_attribute_value_external_code(
                    attribute_id,
                    value.get('value_index'),
                )
                if not attribute_value_id:
                    continue
                attribute_value_ids.append(attribute_value_id)

        # 2. Parse attributes from settings
        attribute_settings_value_ids = list()
        attributes_from_settings = self.get_settings_value('attribute_codes')
        attribute_settings_ids = [x[0] for x in attributes_from_settings if not x[-1]]

        if attribute_settings_ids:
            custom_attributes = self._parse_custom_attributes(product)
            attributes_from_settings_filter = [
                (fk, code) for fk, code, is_default in attributes_from_settings if not is_default
            ]
            attribute_settings_value_ids = self._parse_attribute_values_by_codes(
                attributes_from_settings_filter,
                custom_attributes,
            )

        attribute_ids.extend(attribute_settings_ids)
        attribute_value_ids.extend(attribute_settings_value_ids)
        return list(set(attribute_ids)), list(set(attribute_value_ids))

    def _create_or_update_product(self, client, external_id, data):
        if external_id:
            product = self.fetch_one('products', external_id)
            sku = quote_plus(product['sku'])
            result = client.put(f'products/{sku}', data)
        else:
            result = client.post('products', data)
        return result

    def _get_url_pattern(self, wrap_li=True):
        pattern = (
            f'<a href="{self.admin_url}/catalog/product/edit/id/%s/key/" target="_blank">%s</a>'
        )
        if wrap_li:
            return f'<li>{pattern}</li>'
        return pattern

    def _prepare_url_args(self, record):
        return (record.id, record.format_name)

    def _convert_to_html(self, id_list):
        pattern = self._get_url_pattern()
        arg_list = [self._prepare_url_args(x) for x in id_list]
        return ''.join([pattern % args for args in arg_list])

    @staticmethod
    def _parse_ecommerce_value(magento_product, field_name):
        if not field_name.startswith(f'{CUSTOM_ATTRIBUTES}.'):
            return magento_product.get(field_name)

        attribute_name = field_name.split('.')[-1]
        attributes = magento_product.get(CUSTOM_ATTRIBUTES) or list()
        meta_value = list(filter(lambda x: x['attribute_code'] == attribute_name, attributes))

        if not meta_value:
            return False
        return meta_value[0]['value']

    @staticmethod
    def _convert_type_to_odoo(name):
        return PRODUCT_TYPES.get(name, 'product')

    @staticmethod
    def _parse_product_variants(product):
        return product[EXTENSION_ATTRIBUTES].get('configurable_product_links', [])

    @staticmethod
    def _parse_configurable_options(product):
        return product[EXTENSION_ATTRIBUTES].get('configurable_product_options', [])

    @staticmethod
    def _parse_bundle_options(product):
        return product[EXTENSION_ATTRIBUTES].get('bundle_product_options', [])

    @staticmethod
    def _parse_custom_attributes(product):
        custom_attributes = product.get(CUSTOM_ATTRIBUTES, [])
        return {x['attribute_code']: x['value'] for x in custom_attributes}

    def _default_product_domain(self):
        # Skip BUNDLE and GROUPED
        settings_domain = self.get_settings_value('import_products_filter')
        domain = [('type_id', 'in', ','.join([CONFIGURABLE, SIMPLE, VIRTUAL, DOWNLOADABLE]))]
        return settings_domain + domain

    @staticmethod
    def _parse_product_images(product):
        image_list = list()
        media_list = product.get('media_gallery_entries', [])

        for media in media_list:
            if media.get('media_type') == 'image':
                image_list.append(media)

        return image_list

    @staticmethod
    def _build_attribute_external_code(attribute_data):
        attribute_id = attribute_data['attribute_id']
        attribute_code = attribute_data['attribute_code']
        return f'{attribute_id}-{attribute_code}'

    @staticmethod
    def _parse_attribute_external_code(code):
        attribute_id, attribute_code = code.split('-', 1)
        return attribute_id, attribute_code

    @staticmethod
    def _build_attribute_value_external_code(attribute_code, option_value):
        if not all([attribute_code, option_value]):
            return str()
        return f'{attribute_code}-{option_value}'

    @staticmethod
    def _build_state_external_code(country, state, state_id):
        return f'{country}_{state}({state_id})'

    @staticmethod
    def _parse_attribute_value_external_code(code):
        attribute_code, option_value = code.split('-', 1)
        return attribute_code, option_value

    @staticmethod
    def _generate_url_key(name, template_id, variant_id=None):
        """Generate unique `url_key` for Magento 2 API."""
        formatted_name = escape_trash(name, max_length=300, lowercase=True)
        key = f'{formatted_name}-{template_id}'

        if variant_id:
            return f'{key}-{variant_id}'

        return key

    def _disable_manage_stock(self, magento_product):
        sku = magento_product['sku']
        stock_item_id = magento_product[EXTENSION_ATTRIBUTES]['stock_item']['item_id']

        result = self.apply(
            f'products/{sku}/stockItems/{stock_item_id}',
            data={
                'stock_item': {
                    'use_config_manage_stock': False,
                    'manage_stock': False,
                }
            },
        )
        return result

    def _get_magento_type(self, template):
        multiple_variants = template['variant_count'] > 1

        if template['type'] == 'service':
            magento_type = VIRTUAL
        elif multiple_variants:
            magento_type = CONFIGURABLE
        elif template['kits']:
            magento_type = BUNDLE
        else:
            magento_type = SIMPLE

        return magento_type

    @staticmethod
    def _parse_customer(customer):
        customer_ = {
            'id': str(customer['id']),
            'email': customer['email'],
            'person_name': f'{customer["firstname"]} {customer["lastname"]}',
        }
        return customer_

    @staticmethod
    def _parse_address(customer, magento_address):
        if not magento_address:
            return magento_address

        firstname = magento_address['firstname']
        lastname = magento_address['lastname']

        magento_address_street = magento_address['street']
        street = magento_address_street[0]

        try:
            street2 = magento_address_street[1]
        except IndexError:
            street2 = ''

        try:
            street3 = magento_address_street[2]
        except IndexError:
            pass
        else:
            street2 += f'\n{street3}'

        address = {
            'id': '',
            'person_name': f'{firstname} {lastname}',
            'company_name': magento_address.get('company') or '',
            'company_reg_number': magento_address.get('vat_id') or '',
            'email': customer['email'],
            'street': street,
            'street2': street2,
            'country': magento_address['country_id'],
            'state': str(magento_address.get('region_id', '') or ''),
            'city': magento_address['city'],
            'phone': magento_address['telephone'],
        }

        if magento_address.get('postcode'):
            address['zip'] = magento_address['postcode']

        return address

    def get_shop_weight_uoms_for_converter(self):
        if not self._shop_weight_uoms:
            raise UserError(_(
                'Sale Integration setting "Magento 2 weight units" is not specified. '
                'Please, deactivate and then activate Sale Integration to populate it'))

        result = safe_eval(self._shop_weight_uoms)
        return result

    def get_weight_uoms(self):
        result = []

        if not self._shop_weight_uoms:
            return result

        for uom in safe_eval(self._shop_weight_uoms).values():
            if uom and uom not in result:
                result.append(uom)

        return result
