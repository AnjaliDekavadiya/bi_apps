# See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import _
from odoo.tools.sql import escape_psql
from odoo.exceptions import ValidationError


class MagentoOrderLine:

    def __init__(self, magento_order, line_data):
        self._magento_order = magento_order
        self._line_data = line_data

    def __getattr__(self, name):
        return self._line_data.get(name)

    def __hash__(self):
        return hash(self.item_id)

    def __eq__(self, other_line):
        return isinstance(other_line, MagentoOrderLine) and self.item_id == other_line.item_id

    def __repr__(self):
        return f'{self.__class__.__name__}({self.item_id}, {self.product_type})'

    @property
    def _order(self):
        return self._magento_order

    @property
    def _order_lines(self):
        return self._magento_order._lines

    @property
    def _env(self):
        return self._magento_order._env

    @property
    def _adapter(self):
        return self._magento_order._adapter

    @property
    def _integration_id(self):
        return self._magento_order._integration_id

    @property
    def _integration_name(self):
        return self._magento_order._integration_name

    @property
    def integration(self):
        return self._magento_order.integration

    def get_coupon(self):
        return self._order.coupon_code

    def parse_line(self, child_list):
        parser = getattr(self, f'_parse_{self.product_type}')
        parsed_vals_list = parser(child_list)
        return parsed_vals_list

    def get_parent(self):
        if not self.parent_item_id:
            return False
        lines_hub = {x.item_id: x for x in self._order_lines}
        return lines_hub.get(self.parent_item_id, False)

    def get_odoo_variant(self):
        external_product_id = self.get_external_product()

        if external_product_id:
            code = external_product_id.code
        else:
            code = self._adapter._build_product_external_code(self.product_id)

        odoo_variant = self._env['integration.sale.order.factory']\
            ._try_get_odoo_product(self.integration, dict(product_id=code))
        return odoo_variant

    def get_external_product(self):
        code = self.product_id
        complex_code = self._adapter._build_product_external_code(code)
        external_record_ids = self._env['integration.product.product.external'].search([
            '|',
            ('code', '=', complex_code),
            ('code', '=like', f'%-{code}'),
            ('integration_id', '=', self._integration_id),
        ])

        filter_record_ids = external_record_ids.filtered(lambda x: x.code == complex_code)
        external_id = filter_record_ids or external_record_ids

        if external_id and len(external_id) > 1:
            raise ValidationError(_(
                'Magento 2. There are multiple matches in external table: %s' % external_id
            ))
        return external_id

    def get_tax_options(self):
        all_taxes = self._order.extension_attributes.get('item_applied_taxes', [])
        item_applied_taxes = {
            x['item_id']: x['applied_taxes'] for x in all_taxes if x['type'] == 'product'
        }
        return item_applied_taxes.get(self.item_id, [])

    def get_product_options(self):
        option_list = list()
        product_option = self.product_option or dict()
        extension_attributes = product_option.get('extension_attributes', {})
        custom_options = extension_attributes.get('custom_options', [])

        for option in custom_options:
            option_id = option.get('option_id')
            option_value = option.get('option_value')

            option_str = self._convert_option_to_string(option_id, option_value)
            if option_str:
                option_list.append(option_str)

        return option_list

    def _convert_option_to_string(self, option_id, option_value):
        if not option_id:
            return str()

        product = self._adapter.fetch_one('products', self.product_id)
        option_list = product.get('options', [])
        option_router = {
            str(x['option_id']): (x['title'], x.get('values', [])) for x in option_list
        }

        title, values = option_router.get(option_id, (option_id, []))
        if values:
            value_router = {
                str(x['option_type_id']): x['title'] for x in values
            }
            value = ', '.join(
                filter(None, [value_router.get(x.strip()) for x in option_value.split(',')])
            )
        else:
            value = option_value

        option_str = self._format_option_stirng(title, value)
        return option_str

    @staticmethod
    def _format_option_stirng(title, value):
        if title and value:
            res = f'{title}: {value}'
        elif title and not value:
            res = title
        else:
            res = str()
        return res

    def find_odoo_template_or_create_bom(self, child_list):
        odoo_template = self._find_or_create_odoo_template(child_list)

        if not odoo_template.mrp_enabled:
            raise ValidationError(_(
                'The product %s contains bom-components,'
                'however the Manufacturing module is not installed.'
                % self.name
            ))

        if odoo_template.bom_ids:
            return odoo_template

        odoo_child_ids = [x.get_odoo_variant() for x in child_list]

        bom_line_ids = list()
        for line, odoo_variant in zip(child_list, odoo_child_ids):
            bom_line_ids.append((0, 0, {
                'product_id': odoo_variant.id,
                'product_qty': line.qty_ordered / self.qty_ordered,
            }))

        vals = {
            'type': 'phantom',
            'bom_line_ids': bom_line_ids,
            'product_tmpl_id': odoo_template.id,
        }
        self._env['mrp.bom'].with_context(skip_product_export=True).create(vals)

        return odoo_template

    def _find_or_create_odoo_template(self, child_list):
        ProductTemplate = self._env['product.template']
        product = self._adapter.fetch_one('products', self.product_id)
        fake_reference = self._build_reference_from_childs(product, child_list)
        ref_field = self.integration._get_product_reference_name()

        odoo_template = ProductTemplate.search([
            (ref_field, '=ilike', escape_psql(fake_reference)),
        ], limit=1)

        if not odoo_template:
            vals = {
                'name': product['name'],
                'type': 'product',
                'list_price': product.get('price'),
                'default_code': fake_reference,
                'integration_ids': None,
                'exclude_from_synchronization': True,
            }
            odoo_template = ProductTemplate.with_context(skip_product_export=True).create(vals)

        return odoo_template

    def _parse_simple(self, *args, **kw):
        data = self._parse_default_data()
        external_product = self.get_external_product()

        if external_product:
            code = external_product.code
        else:
            code = self._adapter._build_product_external_code(self.product_id)

        data['product_id'] = code
        return [data]

    def _parse_virtual(self, *args, **kw):
        return self._parse_simple(*args, **kw)

    def _parse_downloadable(self, *args, **kw):
        return self._parse_simple(*args, **kw)

    def _parse_grouped(self, *args, **kw):
        return self._parse_simple(*args, **kw)

    def _parse_configurable(self, child_list):
        data = self._parse_default_data()
        assert len(child_list) == 1, _('Expected single product-variant.')
        child_id = child_list[0]

        data['id'] = str(self.item_id or '')
        code = self._adapter._build_product_external_code(self.product_id, child_id.product_id)
        data['product_id'] = code
        return [data]

    def _parse_bundle(self, child_list):
        assert len(child_list), _('Expected not empty bundle.')
        data = self._parse_default_data()
        odoo_template = self.find_odoo_template_or_create_bom(child_list)

        if not data['taxes']:
            # Actually i don't know from what object i have to parse taxes.
            # One time it contains in parent object second time in child. Time will tell.
            tax_list = self.parse_tax_from_childs(child_list)
            data['taxes'] = tax_list

        data['odoo_variant_id'] = odoo_template.product_variant_id.id
        return [data]

    def _parse_default_data(self):
        data = {
            'id': str(self.item_id or ''),
            'product_id': str(self.product_id),
            'price_unit': self.price,
            'price_unit_tax_incl': self.price_incl_tax,
            'product_uom_qty': self.qty_ordered,
            'taxes': self.parse_line_tax(),
            'discount': self._calculate_line_discount(),
            'add_description_list': list(),
        }

        product_options_list = self.get_product_options()
        if product_options_list:
            data['add_description_list'].append('\n'.join(product_options_list))

        coupone = self.get_coupon()
        if coupone:
            data['add_description_list'].append(f'Coupon: {coupone}')

        return data

    def _calculate_line_discount(self):
        # Don't use `discount_percent` because of the discount may be as a sum of
        # different sub-discounts with own percent rate or fixed amount. And using magento API
        # unfortunately we don't really know from what the parts the final discount consist.
        return self.discount_amount

    def parse_line_tax(self):
        item_taxes = self.get_tax_options()
        name_list = [x['code'] for x in item_taxes]
        return [self._convert_tax_name_to_code(x) for x in name_list]

    def parse_tax_from_childs(self, child_list):
        result = list()

        for child_id in child_list:
            result.extend(child_id.parse_line_tax())

        return result

    def _build_reference_from_childs(self, product, child_list):
        sku_list = [f'{int(x.qty_ordered / self.qty_ordered)}:{x.sku}' for x in child_list]
        return '#'.join([product['sku']] + sku_list)

    def _convert_tax_name_to_code(self, name):
        return self._order._convert_tax_name_to_code(name)


class MagentoOrder:

    def __init__(self, adapter, order_data, env):
        self._adapter = adapter
        self._env = env
        self._integration_id = adapter._integration_id
        self._integration_name = adapter._integration_name
        self._order_data = order_data
        self._lines = self._build_lines()
        self._external_tax_router = self._biuld_external_taxes()

    def __getattr__(self, name):
        return self._order_data.get(name)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.entity_id})'

    @property
    def integration(self):
        return self._env['sale.integration'].browse(self._integration_id)

    def parse_status(self):
        status_list = [self.status]
        shipped = int()
        total_invoiced = self.total_invoiced
        total_qty_ordered = self.total_qty_ordered

        if total_invoiced:
            if total_invoiced == self.grand_total:
                value = 'processing_invoiced'
            else:
                value = 'processing_partially_invoiced'
            status_list.append(value)

        lines_hierarchy = self.lines_hierarchy()
        for line, __ in lines_hierarchy.items():
            shipped += line.qty_shipped

        if shipped:
            if shipped == total_qty_ordered:
                value = 'processing_shipped'
            else:
                value = 'processing_partially_shipped'
            status_list.append(value)

        return status_list

    def parse(self):
        customer = self.parse_customer()

        shipping_address = self.parse_shipping_address(customer)
        if not shipping_address:
            shipping_address.update(customer)

        billing_address = self.parse_billing_address(customer)
        if not billing_address:
            billing_address.update(customer)

        shipping_tax = self.parse_shipping_tax()
        shipping_amount_tax_excl = self.parse_shipping_amount()
        shipping_amount_tax_incl = self.parse_shipping_amount_incl_tax()
        shipping_format = self.parse_shipping_formatted()
        shipping_discount = self.calculate_shipping_discount()

        states = self.parse_status()
        lines = self.parse_lines()

        parsed_order = {
            'id': str(self.entity_id),
            'ref': self.increment_id,
            'date_order': self.created_at,
            'lines': lines,
            'customer': customer,
            'currency': self.order_currency_code,
            'shipping': shipping_address,
            'billing': billing_address,
            'payment_method': self.payment.get('method') or '',
            'amount_total': self.grand_total,
            'delivery_data': {
                'carrier': shipping_format,
                'shipping_cost': shipping_amount_tax_incl,
                'shipping_cost_tax_excl': shipping_amount_tax_excl,
                'taxes': shipping_tax,
                'discount': shipping_discount,
                'delivery_notes': '',
            },
            'discount_data': dict(),
            'gift_data': dict(),
            'current_order_state': self.status,
            'integration_workflow_states': states,
            'order_risks': list(),
            'order_transactions': list(),
            'external_tags': list(),
            'is_cancelled': True if 'canceled' in states else False,
        }
        return parsed_order

    def calculate_shipping_discount(self):
        shipping = self.parse_shipping()
        shipping_discount_amount = shipping['total']['shipping_discount_amount']
        return shipping_discount_amount

    def parse_shipping_formatted(self, to_tuple=False):
        shipping = self.parse_shipping()
        method = shipping.get('method') or ''

        if not method:
            shipping_format = tuple()
        else:
            shipping_format = (('id', method), ('name', method))

        if to_tuple:
            return shipping_format
        return dict(shipping_format)

    def parse_shipping_amount(self):
        shipping = self.parse_shipping()
        return shipping['total']['shipping_amount']

    def parse_shipping_amount_incl_tax(self):
        shipping = self.parse_shipping()
        return shipping['total']['shipping_incl_tax']

    def parse_lines(self):
        result = list()
        lines_hierarchy = self.lines_hierarchy()

        for line, child_list in lines_hierarchy.items():
            parsed_vals_list = line.parse_line(child_list)
            result.extend(parsed_vals_list)

        return result

    def lines_hierarchy(self):
        result = defaultdict(list)

        for line in self._lines:
            parent_line = line.get_parent()

            if parent_line:
                result[parent_line].append(line)
            else:
                result[line] = list()

        return result

    def parse_customer(self):
        customer = {
            'id': str(self.customer_id or ''),
            'email': self.customer_email,
            'person_name': self.prepare_customer_name(),
        }
        return customer

    def prepare_customer_name(self):
        if self.customer_firstname and self.customer_lastname:
            firstname = self.customer_firstname
            lastname = self.customer_lastname
        else:
            # Fallback to customer Billing name for Guest orders created by admin
            firstname = self.billing_address.get('firstname')
            lastname = self.billing_address.get('lastname')

        return f'{firstname} {lastname}'

    def parse_billing_address(self, customer):
        return self._parse_address(customer, self.billing_address)

    def parse_shipping_address(self, customer):
        shipping = self.parse_shipping()
        return self._parse_address(customer, shipping.get('address', {}))

    def parse_shipping_tax(self):
        item_applied_taxes = [
            x for x in self.extension_attributes['item_applied_taxes'] if x['type'] == 'shipping'
        ]
        name_list = [x['code'] for item in item_applied_taxes for x in item['applied_taxes']]
        return [self._convert_tax_name_to_code(x) for x in name_list]

    def parse_shipping(self):
        shipping_assignments = self.extension_attributes['shipping_assignments']
        assert len(shipping_assignments) == 1, 'expected one shipping assignment'
        shipping_assignment = shipping_assignments[0]
        return shipping_assignment.get('shipping', {}) or {}

    def _parse_address(self, customer, magento_address):
        return self._adapter._parse_address(customer, magento_address)

    def _build_lines(self):
        return [MagentoOrderLine(self, item) for item in self.items]

    def _biuld_external_taxes(self):
        external_taxes = self._env['integration.account.tax.external'].search([
            ('integration_id', '=', self._integration_id),
        ])
        return dict([(x.name, x.code) for x in external_taxes])

    def _convert_tax_name_to_code(self, name):
        return self._external_tax_router.get(name, name)
