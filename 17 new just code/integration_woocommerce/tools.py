# See LICENSE file for full copyright and licensing details.

from xml.etree import ElementTree

import requests

from odoo import _
from odoo.exceptions import ValidationError
from odoo.tools.sql import escape_psql
from odoo.addons.integration.tools import xml_to_dict_recursive, flatten_recursive


SET_UP_BUNDLE_OR_COMPOSITE_PRODUCTS_TEXT = """
- Go to Product Data > Shipping and choose the Unassembled Bundle Type.
- Navigate to Product Data > General and make sure that the Regular/Sale Price fields are empty.
- Finally, go to Product Data > Bundled Products (Components) and make sure that at least one
bundled item is Priced Individually."""

BUNDLE_PRODUCT_CONFIG_ERROR = f"""%s: Invalid configuration for bundle (composite) product "%s".
The main price have to be empty.
{SET_UP_BUNDLE_OR_COMPOSITE_PRODUCTS_TEXT}"""

BUNDLE_PRODUCT_FORMAT_ERROR = f"""%s: This "%s" product (id=%s) is a bundle but it added as a
single-line in sales order. That is not allowed for bundle (composite) products. Please go to the
order in WooCommerce and click "Configure" button to fix this issue. After that you will need to
re-import the order (enable checkbox "Update Required" on order in External Orders Data menu).
{SET_UP_BUNDLE_OR_COMPOSITE_PRODUCTS_TEXT}"""


class XmlRpc:

    _headers = {
        'Accept': 'application/xml',
        'Content-Type': 'application/xml',
        'User-Agent': 'Odoo-Ecommerce-Integration/1.0',
    }

    @classmethod
    def send_request(cls, url, method_name, arg_list):
        """
        :param url: endpoint (str)
        :param method_name: method to call by RPC request (str)
        :param arg_list: list of the arguments for the calling method (list)
        """
        data = cls._prepare_xml_data(method_name, arg_list)
        return requests.post(url=url, data=data, headers=cls._headers, verify=False)

    @classmethod
    def xml_string_to_dict(cls, xml_string, root_tag=None):
        root = ElementTree.XML(xml_string)
        if root_tag:
            root = root.find(f'.//{root_tag}')

        if not root:
            return dict()

        xml_dict = xml_to_dict_recursive(root)

        if root_tag:
            return xml_dict.get(root_tag)
        return xml_dict

    @staticmethod
    def _prepare_xml_data(method_name, arg_list):
        xml_param = """
        <param>
            <value>
                <string>%s</string>
            </value>
        </param>
        """
        xml_body = """
        <?xml version="1.0" encoding="UTF-8"?>
        <methodCall>
            <methodName>%s</methodName>
            <params>%s</params>
        </methodCall>
        """
        xml_params = ''.join(xml_param % arg for arg in arg_list)
        return xml_body % (method_name, xml_params)


class WooOrderLine:

    def __init__(self, order: 'WooOrder', data: dict) -> None:
        self._order = order
        self._data = data
        self._product_dict = dict()

    def __getattr__(self, name):
        return self._data.get(name)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.id}, {self.sku})'

    @property
    def integration(self):
        return self._order.integration

    @property
    def env(self):
        return self._order.env

    @property
    def adapter(self):
        return self._order.adapter

    @property
    def quantity_prop(self):
        return int(self.quantity or 1)

    @property
    def price_unit_prop(self):
        return float(self.subtotal) / self.quantity_prop

    @property
    def _is_composite(self):
        return bool(self.composite_children)

    @property
    def _is_bundle(self):
        return bool(self.bundled_items)

    @property
    def _is_child(self):
        return bool(self.composite_parent or self.bundled_by)

    @property
    def _is_simple(self):
        return not (self._is_composite or self._is_bundle or self._is_child)

    @property
    def _parent_id(self):
        return self.bundled_by or self.composite_parent or False

    @property
    def _child_ids(self):
        if self._is_composite:
            return self.composite_children

        if self._is_bundle:
            return self.bundled_items

        return list()

    @property
    def product_dict(self):
        if not self._product_dict:
            self._product_dict = self.adapter.fetch_one(
                f'products/{self.product_id}',
                params=self.adapter.prepare_lang_param(),
            )
        assert self._product_dict, _('External product %s not found') % self.product_id
        return self._product_dict

    def get_parent(self):
        parent_id = self._parent_id
        if parent_id:
            return self._get_line_by_id(parent_id)
        return False

    def get_childs(self):
        return [self._get_line_by_id(x) for x in self._child_ids]

    def parse_line_recursively(self):
        # 1. Ensure empty price for parent (self) if it's a bundles/composite product
        if self._child_ids and self.price_unit_prop:
            raise ValidationError(
                BUNDLE_PRODUCT_CONFIG_ERROR % (self.integration.name, f'({self.id}) {self.name}')
            )

        data = self._parse_order_row()

        # 2. Parse bundle/composite products
        if self._child_ids:
            # 2.1 Create kit
            if self.integration.allow_bundle_creation:
                odoo_template = self._find_odoo_template_or_create_bom()
                data.update(
                    price_unit=self._get_price_recursively(),
                    odoo_variant_id=odoo_template.product_variant_id.id,
                )
                return data
            # 2.2 Decompose to simple components
            return [self._parse_line_by_id(x) for x in self._child_ids]

        # 3. If external product exists - this one definitely a simple Woo product
        # because of we are not creating mappings for bundles/composites
        external_id = self._get_external_product()
        if external_id:
            return data

        # 4. Return if the bundles/composites products plugin isn't installed
        if not self.adapter.accept_nested_products:
            return data

        # 5. Raise if this one is a bundle/composition product formatted as a single-line
        template_type = self.product_dict.get('type')

        if template_type in ('bundle', 'composite'):
            # TODO: Download the standard version of product
            raise ValidationError(
                BUNDLE_PRODUCT_FORMAT_ERROR
                % (self.integration.name, template_type, f'({self.id}) {self.name}')
            )

        return data

    def _parse_order_row(self):
        subtotal = float(self.subtotal)
        subtotal_tax = float(self.subtotal_tax)
        total = float(self.total)

        return {
            'id': str(self.id),
            'product_id': self.adapter._build_product_external_code(
                self.product_id,
                self.variation_id,
            ),
            'product_uom_qty': self.quantity_prop,
            # Price per unit without taxes
            'price_unit': self.price_unit_prop,
            # Price per unit with taxes
            'price_unit_tax_incl': (subtotal + subtotal_tax) / self.quantity_prop,
            'taxes': [str(x['id']) for x in self.taxes],
            # Discount without taxes
            'discount': (subtotal - total),
            # Discount with taxes
            'discount_tax_incl': (subtotal + subtotal_tax) - (total + float(self.total_tax)),
        }

    def _find_odoo_template_or_create_bom(self):
        # If we are here it means the current one definetly has the `child_ids` and
        # `integration.allow_bundle_creation` property is ON
        odoo_template = self._find_or_create_odoo_template()

        if not odoo_template.mrp_enabled:
            raise ValidationError(_(
                'The product %s contains bom-components,'
                'however the Manufacturing module is not installed.'
                % self.name
            ))

        if odoo_template.bom_ids:
            return odoo_template

        child_list = self.get_childs()
        variant_list = [x._get_odoo_variant() for x in child_list]

        bom_line_ids = list()
        for line, odoo_variant in zip(child_list, variant_list):
            bom_line_ids.append((0, 0, {
                'product_id': odoo_variant.id,
                'product_qty': line.quantity_prop / self.quantity_prop,
            }))

        self.env['mrp.bom'].with_context(skip_product_export=True).create({
            'type': 'phantom',
            'bom_line_ids': bom_line_ids,
            'product_tmpl_id': odoo_template.id,
        })

        return odoo_template

    def _get_odoo_variant(self):
        if self._child_ids:
            # 1. Ensure empty price for parent (self) if it's a bundles/composite product
            if self.price_unit_prop:
                raise ValidationError(
                    BUNDLE_PRODUCT_CONFIG_ERROR
                    % (self.integration.name, f'({self.id}) {self.name}')
                )
            odoo_template = self._find_odoo_template_or_create_bom()
            return odoo_template.product_variant_id

        external_product_id = self._get_external_product()

        if external_product_id:
            code = external_product_id.code
        else:
            code = self.adapter._build_product_external_code(self.product_id, self.variation_id)

        # Create product no matter on the `auto_create_products_on_so` property (force_create=True)
        odoo_variant = self.env['integration.sale.order.factory']._try_get_odoo_product(
            self.integration,
            dict(product_id=code),
            force_create=True,
        )
        return odoo_variant

    def _get_external_product(self):
        code = self.adapter._build_product_external_code(self.product_id, self.variation_id)
        return self.env['integration.product.product.external'].search([
            ('code', '=', code),
            ('integration_id', '=', self.integration.id),
        ], limit=1)

    def _parse_line_by_id(self, line_id):
        line = self._get_line_by_id(line_id)
        return line.parse_line_recursively()

    def _get_line_by_id(self, line_id):
        return list(filter(lambda x: x.id == line_id, self._order._lines))[0]

    def _find_or_create_odoo_template(self):
        fake_reference = self._build_reference_from_childs()
        ref_field = self.integration._get_product_reference_name()

        odoo_template = self.env['product.template'].search([
            (ref_field, '=ilike', escape_psql(fake_reference)),
        ], limit=1)

        if not odoo_template:
            vals = {
                'name': self.product_dict['name'],
                'type': 'product',
                'list_price': self.product_dict.get('regular_price'),
                'default_code': fake_reference,
                'integration_ids': None,
                'exclude_from_synchronization': True,
            }
            odoo_template = self.env['product.template'].\
                with_context(skip_product_export=True).create(vals)

        return odoo_template

    def _get_price_recursively(self):
        nested_list = [x._get_price() for x in self.get_childs()]
        return sum(flatten_recursive(nested_list)) / self.quantity_prop

    def _get_price(self):
        if self._child_ids:
            return [x._get_price() for x in self.get_childs()]
        return float(self.subtotal)

    def _get_sku_or_complex_code(self):
        if self.sku:
            return self.sku

        code = self.adapter._build_product_external_code(self.product_id, self.variation_id)

        external = self.env['integration.product.product.external'].search([
            ('integration_id', '=', self.integration.id),
            ('code', '=', code),
        ], limit=1)

        return external.external_reference or code

    def _parse_references(self):
        result = list()

        code = self._get_sku_or_complex_code()

        if self._parent_id:
            parent = self.get_parent()
            result.append(f'{int(self.quantity_prop / parent.quantity_prop)}:{code}')
        else:
            result.append(code)

        if self._child_ids:
            result.append([x._parse_references() for x in self.get_childs()])

        return result

    def _build_reference_from_childs(self):
        return '#'.join(flatten_recursive(self._parse_references()))

    def _line_info(self):
        data = dict(
            name=self.name,
            sku=self.sku,
            quantity=self.quantity_prop,
            subtotal=float(self.subtotal),
            parent_id=getattr(self.get_parent(), 'id', False),
            code=self.adapter._build_product_external_code(self.product_id, self.variation_id),
        )

        if self._child_ids:
            data['childs'] = [x._line_info() for x in self.get_childs()]

        return {self.id: data}


class WooOrder:

    def __init__(self, integration, data: dict) -> None:
        self.integration = integration
        self._data = data
        self._lines = [WooOrderLine(self, item) for item in self.line_items]

    def __repr__(self):
        return f'<{self.integration.name}>: Order({self.id})'

    def __getattr__(self, name):
        return self._data.get(name)

    @property
    def env(self):
        return self.integration.env

    @property
    def adapter(self):
        return self.integration.adapter

    def get_sorted_lines(self):
        return self._get_composite_lines() + self._get_bundle_lines() + self._get_simple_lines()

    def parse(self):
        lines = self.parse_lines()
        payment_transactions = self._parse_payment_transactions()
        delivery_data = self._parse_delivery_data()
        fee_data = self._parse_fee_lines()

        parsed_order = {
            'id': str(self.id),
            'ref': self.number,
            'current_order_state': self.status,
            'date_order': self.date_created_gmt,
            'integration_workflow_states': [self.status],
            'currency': self.currency,
            'lines': lines,
            'payment_method': self.payment_method,
            'payment_transactions': payment_transactions,
            'amount_total': float(self.total),
            'delivery_data': delivery_data,
            'discount_data': dict(),
            'gift_data': dict(),
            'fee_data': fee_data,
            'order_risks': list(),
            'order_transactions': list(),
            'external_tags': list(),
            'is_cancelled': True if self.status == 'cancelled' else False,
        }

        customer_data = dict()
        metadata = self.meta_data or []

        if self.billing:
            customer_data['email'] = self.billing['email']

        if self.customer_id:
            raw_customer = self.adapter.fetch_one(f'customers/{self.customer_id}')

            if raw_customer:
                customer_data = self.adapter._parse_customer(raw_customer)

                # Replace customer language with language from order metadata.
                # This allows to set correct language based on site language
                # when customer placed an order
                language = self.adapter._get_meta_date_value(metadata, 'wpml_language')  # TODO
                if language and self.integration.set_customer_language_based_on_orders_metadata:
                    customer_data['language'] = language

                parsed_order['customer'] = customer_data

        vat_metafield = self.integration.woocommerce_vat_metafield_field_name

        if self.shipping:
            parsed_order['shipping'] = self.adapter._parse_address(
                customer_data, self.shipping, 'delivery', vat_metafield, metadata)

        if self.billing:
            parsed_order['billing'] = self.adapter._parse_address(
                customer_data, self.billing, 'invoice', vat_metafield, metadata)

        return parsed_order

    def parse_lines(self):
        nested_list = [x.parse_line_recursively() for x in self.get_sorted_lines()]
        return flatten_recursive(nested_list)

    def get_lines_hierarchy(self):
        """Debug method"""
        return [x._line_info() for x in self.get_sorted_lines()]

    # TODO Payments in WC implemented by plugins. Maybe we should customize it
    def _parse_payment_transactions(self):
        transaction = []

        if self.date_paid and self.transaction_id:
            transaction.append({
                'transaction_id': f'{self.id} ({self.payment_method}): {self.transaction_id}',
                'transaction_date': self.date_paid,
                'amount': float(self.total),  # TODO May be wrong
                'currency': self.currency,  # TODO May be wrong
            })

        return transaction

    def _parse_delivery_data(self):
        result = {
            'carrier': {},
            'shipping_cost': 0,
            'delivery_notes': self.customer_note,
        }

        if self.shipping_lines:
            shipping = self.shipping_lines[0]

            carrier_tax_rate = 0
            if float(shipping['total']):
                carrier_tax_rate = float(shipping['total_tax']) * 100 / float(shipping['total'])

            shipping_method_id = shipping['instance_id']

            # If the order was created in WooCommerce admin, instance_id will be 0. In this case,
            # we need to use method_id to get the shipping method ID.
            if shipping['instance_id'] == '0':
                if shipping['method_id']:
                    shipping_method_id = shipping['method_id']
                else:
                    # For orders created through the Woocommerce admin panel, it is possible to
                    # add a shipping method that is not available in WooCommerce. To create
                    # orders correctly in Odoo, we use the method_title to create the delivery
                    # method.
                    shipping_method_id = shipping['method_title']

            result.update({
                'carrier_tax_rate': carrier_tax_rate,
                'shipping_cost_tax_excl': float(shipping['total']),
                'shipping_cost': float(shipping['total']) + float(shipping['total_tax']),
                'taxes': [str(x['id']) for x in shipping['taxes']],
                'carrier': {
                    'id': shipping_method_id,
                    'name': shipping['method_title'],
                },
            })

        return result

    def _parse_fee_lines(self):
        return [
            {
                'name': line['name'],
                'tax_class': line['tax_class'],
                'total': float(line['total']),
                'total_tax': float(line['total_tax']),
                'taxes': line['taxes'],
            } for line in self.fee_lines
        ]

    def _get_composite_lines(self):
        return sorted(
            filter(lambda x: x._is_composite and not x._is_child, self._lines),
            key=lambda x: x.id,
        )

    def _get_bundle_lines(self):
        return sorted(
            filter(lambda x: x._is_bundle and not x._is_child, self._lines),
            key=lambda x: x.id,
        )

    def _get_simple_lines(self):
        return sorted(
            filter(lambda x: x._is_simple, self._lines),
            key=lambda x: x.id,
        )
