#  See LICENSE file for full copyright and licensing details.

from copy import deepcopy

from odoo import api
from odoo import models, fields
from odoo.exceptions import ValidationError

from ..magento2.exceptions import Magento2ApiException


ORDER_STATUS = {
    'processing': (
        'Processing',
        'When the state of new orders is set to `Processing`, the Automatically Invoice All Items '
        'option becomes available in the configuration. Invoices are not created automatically '
        'for orders placed by using Gift Card, Store Credit, Reward Points, '
        'or other offline payment methods.',
    ),
    'fraud': (
        'Suspected Fraud',
        'Sometimes orders paid via PayPal or another payment gateway are marked as Suspected '
        'Fraud. This means the order does not have invoice issued and the confirmation email '
        'is also not sent.',
    ),
    'pending_payment': (
        'Pending Payment',
        'This is the status used if order is created and PayPal or similar payment method is used. '
        'This means that the customer was directed to the payment gateway website, '
        'but no return information has been received yet. This status will change when '
        'customer pays.',
    ),
    'payment_review': (
        'Payment Review',
        'This status appears when PayPal payment review is turned on.',
    ),
    'pending': (
        'Pending',
        'This status means no invoice and shipments have been submitted.',
    ),
    'holded': (
        'On Hold',
        'This status can only be assigned manually. You can put any order on hold.',
    ),
    'STATE_OPEN': (
        'Open',
        'This status means that an order or credit memo is still open and may need further action.',
    ),
    'processing_shipped': (
        'Order Shipped',
        'This is a simulated order status. Originally it\'s not represented in Magento 2.',
    ),
    'processing_partially_shipped': (
        'Order Partially Shipped',
        'This is a simulated order status. Originally it\'s not represented in Magento 2.',
    ),
    'processing_invoiced': (
        'Order Invoiced',
        'This is a simulated order status. Originally it\'s not represented in Magento 2.',
    ),
    'processing_partially_invoiced': (
        'Order Partially Invoiced',
        'This is a simulated order status. Originally it\'s not represented in Magento 2.',
    ),
    'complete': (
        'Complete',
        'This status means that the order is created, paid, and shipped to customer.',
    ),
    'closed': (
        'Closed',
        'This status indicates that an order was assigned a credit memo and the customer'
        'has received a refund.',
    ),
    'canceled': (
        'Canceled',
        'This status is assigned manually in the Admin or, for some payment gateways, '
        'when the customer does not pay within the specified time.',
    ),
    'paypay_canceled_reversal': (
        'PayPal Canceled Reversal',
        'This status means that PayPal canceled the reversal.',
    ),
    'pending_paypal': (
        'Pending PayPal',
        'This status means that the order was received by PayPal,'
        'but payment has not yet been processed.',
    ),
    'paypal_reversed': (
        'PayPal Reversed',
        'This status means that PayPal reversed the transaction.',
    ),
}
ORDER_STATUS_EXCLUDES = [
    'processing_shipped',
    'processing_partially_shipped',
    'processing_invoiced',
    'processing_partially_invoiced',
]

location_step = ('step_location_id', 'Step 9. Select default Inventory Location')


class QuickConfigurationMagento(models.TransientModel):
    _name = 'configuration.wizard.magento'
    _inherit = 'configuration.wizard'
    _description = 'Quick Configuration for Magento 2'
    _steps = [
        ('step_url', 'Step 1. Enter Webservice Url, User and Key'),
        ('step_shops', 'Step 2. Shops'),
        ('step_languages', 'Step 3. Languages Mapping'),
        ('step_tax_group', 'Step 3. Configure Default Taxes for each Tax Class'),
        ('step_order_status', 'Step 4. Select Order Sub-Statuses for the Receive Order Filter'),
        ('step_product_category_id', 'Step 5. Select Default Product Category ID.'),
        ('step_attribute_set_id', 'Step 6. Select Default Attribute Set ID.'),
        ('step_attribute_group_id', 'Step 7. Select Default Attribute Group ID.'),
        ('step_product_attributes', 'Step 8. Mark Product Attributes as essential.'),
        location_step,
        ('step_finish', 'Finish'),
    ]

    state = fields.Char(
        default='step_url',
    )
    url = fields.Char(
        string='Shop Url',
    )
    key = fields.Char(
        string='Access Token',
    )
    admin_url = fields.Char(
        string='Admin Url',
        help='This URL us needed in order to provide quick links to products '
             'in admin console after validation of products happened.'
    )
    configuration_store_ids = fields.One2many(
        comodel_name='configuration.wizard.magento.line',
        inverse_name='configuration_wizard_id',
        string='Stores',
        domain=lambda self: [
            ('line_type', '=', 'is_store'),
            ('configuration_wizard_id', '=', self.id),
        ],
    )
    configuration_order_status_ids = fields.One2many(
        comodel_name='configuration.wizard.magento.line',
        inverse_name='configuration_wizard_id',
        string='Order Statuses',
        domain=lambda self: [
            ('line_type', '=', 'is_order_status'),
            ('configuration_wizard_id', '=', self.id),
        ],
    )
    configuration_tax_group_ids = fields.One2many(
        comodel_name='configuration.wizard.magento.tax.group',
        inverse_name='configuration_wizard_id',
        string='Taxes for Each Tax Class',
    )
    product_category_id = fields.Many2one(
        comodel_name='configuration.wizard.magento.line',
        string='Product Category ID',
        domain=lambda self: [
            ('line_type', '=', 'is_category'),
            ('configuration_wizard_id', '=', self.id),
        ],
    )
    attribute_set_id = fields.Many2one(
        comodel_name='configuration.wizard.magento.line',
        string='Attribute Set ID',
        domain=lambda self: [
            ('line_type', '=', 'is_attribute_set'),
            ('configuration_wizard_id', '=', self.id),
        ],
    )
    attribute_set_external_id = fields.Integer(
        related='attribute_set_id.external_id',
    )
    attribute_group_id = fields.Many2one(
        comodel_name='configuration.wizard.magento.line',
        string='Attribute Group ID',
        domain=lambda self: [
            ('line_type', '=', 'is_attribute_group'),
            ('configuration_wizard_id', '=', self.id),
        ],
    )
    location_id = fields.Many2one(
        comodel_name='configuration.wizard.magento.line',
        string='Inventory Location',
        domain=lambda self: [
            ('line_type', '=', 'is_inventory_location'),
            ('configuration_wizard_id', '=', self.id),
        ],
    )
    configuration_magento_attribute_ids = fields.One2many(
        comodel_name='configuration.wizard.magento.line',
        inverse_name='configuration_wizard_id',
        string='Magento Attribites',
        domain=lambda self: [
            ('line_type', '=', 'is_attribute'),
            ('configuration_wizard_id', '=', self.id),
        ],
    )
    configuration_magento_line_ids = fields.One2many(
        comodel_name='configuration.wizard.magento.line',
        inverse_name='configuration_wizard_id',
        string='Configuration Magento Lines',
        domain=lambda self: [
            ('configuration_wizard_id', '=', self.id),
        ],
    )

    def get_steps(self):
        steps = super(QuickConfigurationMagento, self).get_steps()
        steps_copy = deepcopy(steps)
        if not self.integration_id.advanced_inventory():
            steps_copy.remove(location_step)
        return steps_copy

    @api.onchange('configuration_magento_attribute_ids')
    def _onchange_set_readonly(self):
        attr_records = self.configuration_magento_attribute_ids
        active_attr_records = attr_records.filtered('activate')
        for rec in active_attr_records:
            rec.set_readonly = False

        passive_records = attr_records - active_attr_records
        active_names = active_attr_records.mapped(lambda x: x.name)
        active_names_lower = [x.lower() for x in active_names if x]
        for rec in passive_records:
            value = False
            if rec.name.lower() in active_names_lower:
                value = True
            rec.set_readonly = value

    # Step Url
    def run_before_step_url(self):
        self.url = self.integration_id.get_settings_value('url')
        self.admin_url = self.integration_id.get_settings_value('admin_url')
        self.key = self.integration_id.get_settings_value('key')

    def run_after_step_url(self):
        self.integration_id.set_settings_value('url', self.url)
        self.integration_id.set_settings_value('admin_url', self.admin_url)
        self.integration_id.set_settings_value('key', self.key)

        self.integration_id.increment_sync_token()

        try:
            self.integration_id.action_active()
        except Magento2ApiException as ex:
            raise ValidationError(ex.name)

        return True

    # Step Shops
    def run_before_step_shops(self):
        if self.configuration_store_ids:
            return

        vals_list = list()
        adapter = self.integration_id._build_adapter()

        for store in adapter.stores_all():
            vals = {
                'line_type': 'is_store',
                'external_id': store['id'],
                'code': store['code'],
                'info': f'{store["locale"]}, {store["base_currency_code"]}',
                'configuration_wizard_id': self.id,
            }
            vals_list.append(vals)

        lines = self.env['configuration.wizard.magento.line'].create(vals_list)

        existing_value = self.integration_id.get_settings_value(
            'shop_ids',
        )
        if existing_value:
            shop_list = list(map(int, existing_value.split(',')))
            lines.filtered(lambda x: x.external_id in shop_list).write({
                'activate': True,
            })

    def run_after_step_shops(self):
        shop_ids = self.configuration_store_ids.filtered('activate')
        self.integration_id.set_settings_value(
            'shop_ids',
            ','.join([str(x.external_id) for x in shop_ids]),
        )
        # Fill weight_uom in settings
        self.integration_id.action_active()
        return True

    # Step Tax Group
    def run_before_step_tax_group(self):
        self.integration_id.initial_import_taxes()
        self.configuration_tax_group_ids.unlink()

        values_list = list()
        default_vals = dict(configuration_wizard_id=self.id)

        tax_group_ids = self.env['integration.account.tax.group.external'].search([
            ('integration_id', '=', self.integration_id.id),
        ])
        for tax_group in tax_group_ids:
            values = {
                **default_vals,
                'external_tax_group_id': tax_group.id,
                'default_external_tax_id': tax_group.default_external_tax_id.id,
                'sequence': tax_group.sequence,
            }
            values_list.append(values)

        self.env['configuration.wizard.magento.tax.group'].create(values_list)

    def run_after_step_tax_group(self):
        for line in self.configuration_tax_group_ids:
            tax_group = line.external_tax_group_id
            tax_group.default_external_tax_id = line.default_external_tax_id.id
            tax_group.sequence = line.sequence

        return True

    # Step Order Status
    def run_before_step_order_status(self):
        if self.configuration_order_status_ids:
            return

        vals_list = list()
        for code, (name, info) in ORDER_STATUS.items():
            if code in ORDER_STATUS_EXCLUDES:
                continue
            vals = {
                'line_type': 'is_order_status',
                'activate': False,
                'name': name,
                'code': code,
                'info': info,
                'configuration_wizard_id': self.id,
            }
            vals_list.append(vals)

        lines = self.env['configuration.wizard.magento.line'].create(vals_list)

        existing_value = self.integration_id.get_settings_value(
            'receive_order_statuses',
        )
        if existing_value:
            status_list = existing_value.split(',')
            lines.filtered(lambda x: x.code in status_list).write({
                'activate': True,
            })

    def run_after_step_order_status(self):
        status_ids = self.configuration_order_status_ids.filtered('activate')
        if not status_ids:
            return True

        self.integration_id.set_settings_value(
            'receive_order_statuses',
            ','.join([x.code for x in status_ids]),
        )

        return True

    # Step Product Category ID
    def run_before_step_product_category_id(self):
        if self.configuration_magento_line_ids.filtered(lambda x: x.line_type == 'is_category'):
            return

        vals_list = list()
        adapter = self.integration_id._build_adapter()
        categories = adapter.fetch_multi('categories/list', domain=[])

        for category in categories['items']:
            if 'name' not in category or 'id' not in category:
                continue

            vals = {
                'line_type': 'is_category',
                'external_id': category['id'],
                'name': category['name'],
                'configuration_wizard_id': self.id,
            }
            vals_list.append(vals)

        lines = self.env['configuration.wizard.magento.line'].create(vals_list)

        existing_value = self.integration_id.get_settings_value(
            'default_product_category_id',
        )
        if existing_value:
            line = lines.filtered(lambda x: x.external_id == int(existing_value))
            self.product_category_id = line.id

    def run_after_step_product_category_id(self):
        self.integration_id.set_settings_value(
            'default_product_category_id',
            str(self.product_category_id.external_id),
        )
        return True

    # Step Attribute Set ID
    def run_before_step_attribute_set_id(self):
        if self.configuration_magento_line_ids.filtered(
            lambda x: x.line_type == 'is_attribute_set'
        ):
            return

        vals_list = list()
        adapter = self.integration_id._build_adapter()
        attribute_sets = adapter.fetch_multi('products/attribute-sets/sets/list', domain=[])

        for attribute in attribute_sets['items']:
            vals = {
                'line_type': 'is_attribute_set',
                'external_id': attribute['attribute_set_id'],
                'name': attribute['attribute_set_name'],
                'configuration_wizard_id': self.id,
            }
            vals_list.append(vals)

        lines = self.env['configuration.wizard.magento.line'].create(vals_list)

        existing_value = self.integration_id.get_settings_value(
            'default_attribute_set_id',
        )
        if existing_value:
            line = lines.filtered(lambda x: x.external_id == int(existing_value))
            self.attribute_set_id = line.id

    def run_after_step_attribute_set_id(self):
        self.integration_id.set_settings_value(
            'default_attribute_set_id',
            str(self.attribute_set_id.external_id),
        )
        return True

    # Step Attribute Group ID
    def run_before_step_attribute_group_id(self):
        existing_value = self.integration_id.get_settings_value(
            'default_attribute_group_id',
        )
        lines = self.configuration_magento_line_ids\
            .filtered(lambda x: x.line_type == 'is_attribute_group')
        if lines and existing_value:
            line = lines.filtered(
                lambda x: x.code == existing_value
                and x.external_id == self.attribute_set_external_id
            )
            self.attribute_group_id = line.id
            return

        vals_list = list()
        adapter = self.integration_id._build_adapter()
        attribute_sets = adapter.fetch_multi('products/attribute-sets/groups/list', domain=[])

        for attribute in attribute_sets['items']:
            vals = {
                'line_type': 'is_attribute_group',
                'external_id': attribute['attribute_set_id'],
                'code': attribute['attribute_group_id'],
                'name': attribute['attribute_group_name'],
                'configuration_wizard_id': self.id,
            }
            vals_list.append(vals)

        lines = self.env['configuration.wizard.magento.line'].create(vals_list)

        if existing_value:
            line = lines.filtered(
                lambda x: x.code == existing_value
                and x.external_id == self.attribute_set_external_id
            )
            self.attribute_group_id = line.id

    def run_after_step_attribute_group_id(self):
        self.integration_id.set_settings_value(
            'default_attribute_group_id',
            self.attribute_group_id.code,
        )
        return True

    # Step Product Attributes
    def run_before_step_product_attributes(self):
        lines = self.configuration_magento_attribute_ids
        adapter = self.integration_id._build_adapter()
        attribute_config_ids = adapter._fetch_attribute_ids_from_configurable_products()

        if not lines:
            vals_list = list()
            field_list = [
                'attribute_id', 'attribute_code', 'default_frontend_label', 'options', 'is_visible',
            ]
            attributes = adapter.fetch_multi('products/attributes', domain=[], fields=field_list)

            for attribute in attributes['items']:
                if not attribute.get('is_visible'):
                    continue
                if not attribute.get('options'):
                    continue
                info = (
                    ', '.join([x['label'] for x in attribute['options'] if x['label'].strip()])
                )
                if not info:
                    continue

                vals = {
                    'line_type': 'is_attribute',
                    'external_id': attribute['attribute_id'],
                    'code': attribute['attribute_code'],
                    'name': attribute['default_frontend_label'],
                    'info': info,
                    'configuration_wizard_id': self.id,
                }
                vals_list.append(vals)

            lines = self.env['configuration.wizard.magento.line'].create(vals_list)

        existing_value = self.integration_id.get_settings_value('attribute_codes')

        lines.write({'activate': False})
        attribute_setting_ids = [int(x[0]) for x in existing_value]
        lines.filtered(lambda x: x.external_id in attribute_setting_ids).write({
            'activate': True,
        })
        attribute_config_ids = [int(x) for x in attribute_config_ids]
        lines.filtered(lambda x: x.external_id in attribute_config_ids).write({
            'activate': True,
            'is_default': True,
        })
        self._onchange_set_readonly()

    def run_after_step_product_attributes(self):
        attribute_ids = self.configuration_magento_attribute_ids.filtered('activate')

        self.integration_id.set_settings_value(
            'attribute_codes',
            [(str(x.external_id), x.code, int(x.is_default)) for x in attribute_ids],
        )
        return True

    # Step Inventory Location
    def run_before_step_location_id(self):
        if self.configuration_magento_line_ids.filtered(
            lambda x: x.line_type == 'is_inventory_location'
        ):
            return

        vals_list = list()
        adapter = self.integration_id.adapter
        locations = adapter.get_locations()

        for rec in locations:
            vals = {
                'name': rec['name'],
                'code': rec['id'],
                'line_type': 'is_inventory_location',
                'configuration_wizard_id': self.id,
            }
            vals_list.append(vals)

        lines = self.env['configuration.wizard.magento.line'].create(vals_list)

        existing_value = self.integration_id.get_settings_value(
            'default_location_id',
        )
        if existing_value:
            line = lines.filtered(lambda x: x.code == existing_value)
            self.location_id = line.id

    def run_after_step_location_id(self):
        self.integration_id.set_settings_value(
            'default_location_id',
            self.location_id.code,
        )
        return True

    @staticmethod
    def get_form_xml_id():
        return 'integration_magento2.view_configuration_wizard'


class QuickConfigurationMagentoTaxGroup(models.TransientModel):
    _name = 'configuration.wizard.magento.tax.group'
    _inherit = 'configuration.wizard.tax.group.abstract'
    _description = 'Quick Configuration Magento Tax Group'

    sequence = fields.Integer(
        help=(
            'When exporting from Odoo to Magento, take the most priority item first '
            'in Order to define which Odoo Tax correspond to which tax group.'
        ),
    )
    configuration_wizard_id = fields.Many2one(
        comodel_name='configuration.wizard.magento',
    )
    external_tax_group_id = fields.Many2one(
        string='Magento External Tax Class',
    )
    default_external_tax_id = fields.Many2one(
        string='Default External Tax',
    )


class QuickConfigurationMagentoLine(models.TransientModel):
    _name = 'configuration.wizard.magento.line'
    _description = 'Quick Configuration Magento Line'
    _order = 'sequence, id'

    sequence = fields.Integer(
        string='Priority',
    )
    activate = fields.Boolean(
        string='Activate',
    )
    external_id = fields.Integer(
        string='External ID',
    )
    name = fields.Char(
        string='Name',
    )
    code = fields.Char(
        string='Code',
    )
    info = fields.Char(
        string='Info',
    )
    is_default = fields.Boolean(
        string='Is Default',
    )
    set_readonly = fields.Boolean(
        string='Set Readonly',
    )
    line_type = fields.Selection(
        selection=[
            ('is_store', 'Is Store'),
            ('is_order_status', 'Is Order Status'),
            ('is_category', 'Is Category'),
            ('is_attribute_set', 'Is Attribute Set'),
            ('is_attribute_group', 'Is Attribute Group'),
            ('is_attribute', 'Is Attribute'),
            ('is_inventory_location', 'Is Location'),
        ],
        string='Line Type'
    )
    configuration_wizard_id = fields.Many2one(
        comodel_name='configuration.wizard.magento',
        ondelete='cascade',
    )
