#  See LICENSE file for full copyright and licensing details.

import re

from odoo import models, fields, _
from odoo.exceptions import UserError

from ..tools import XmlRpc
from ..woocommerce_api_client import TAX_CLASSES
from ..client.exceptions import WooCommerceApiException


class QuickConfigurationWooCommerce(models.TransientModel):
    _name = 'configuration.wizard.woocommerce'
    _inherit = 'configuration.wizard'
    _description = 'Quick Configuration for WooCommerce'
    _steps = [
        ('step_url', 'Step 1. Enter Webservice Url and Key'),
        ('step_api', 'Step 2. API Read and Write Access Check'),
        ('step_wc_languages', 'Step 3. Languages Mapping'),
        ('step_tax_group', 'Step 4. Configure Default Taxes for each Tax Rule'),
        ('step_order_status', 'Step 5. Sales Orders statuses management'),
        ('step_finish', 'Finish')
    ]

    state = fields.Char(
        default='step_url',
    )
    url = fields.Char(
        string='Shop Url',
    )
    admin_url = fields.Char(
        string='Admin Url',
        help='This URL us needed in order to provide quick links to products '
             'in admin console after validation of products happened'
    )
    consumer_key = fields.Char(
        string='Consumer Key',
    )
    consumer_secret = fields.Char(
        string='Consumer Secret',
    )

    verify_ssl = fields.Boolean(
        string="Verify SSL",
        help="WooCommerce is using SSL certificate"
    )

    wp_user = fields.Char(
        string='WordPress User',
    )
    wp_app_password = fields.Char(
        string='WordPress User Application Password',
    )

    configuration_tax_group_ids = fields.One2many(
        comodel_name='configuration.wizard.woocommerce.tax.group',
        inverse_name='configuration_wizard_id',
        string='Taxes for Each Tax Rule',
    )
    order_status_ids = fields.Many2many(
        comodel_name='integration.sale.order.sub.status.external',
        string='Receive Orders in Status',
        relation='configuration_wizard_woocommerce_status_rel',
        domain='[("integration_id", "=", integration_id)]',
    )

    api_permissions_read = fields.Boolean(
        string='Read Permissions',
        readonly=True,
    )
    api_permissions_write = fields.Boolean(
        string='Write Permissions',
        readonly=True,
    )

    # Step Url
    def run_before_step_url(self):
        self.url = self.integration_id.get_settings_value('url')
        self.admin_url = self.integration_id.get_settings_value('admin_url')
        self.consumer_key = self.integration_id.get_settings_value('consumer_key')
        self.consumer_secret = self.integration_id.get_settings_value('consumer_secret')
        self.wp_user = self.integration_id.get_settings_value('wp_user')
        self.wp_app_password = self.integration_id.get_settings_value('wp_app_password')
        self.verify_ssl = self.integration_id.get_settings_value('verify_ssl')

    @staticmethod
    def add_index_php(url):
        if not url.endswith('/'):
            url += '/'

        if not url.endswith('index.php/'):
            url += 'index.php/'

        return url

    def run_after_step_url(self):
        self.integration_id.set_settings_value('url', self.url)
        self.integration_id.set_settings_value('admin_url', self.admin_url)
        self.integration_id.set_settings_value('consumer_key', self.consumer_key)
        self.integration_id.set_settings_value('consumer_secret', self.consumer_secret)
        self.integration_id.set_settings_value('wp_user', self.wp_user)
        self.integration_id.set_settings_value('wp_app_password', self.wp_app_password)
        self.integration_id.set_settings_value('verify_ssl', self.verify_ssl, to_string=True)

        self.integration_id.increment_sync_token()

        try:
            self.integration_id._build_adapter()
        except WooCommerceApiException as e:
            if e.error_code != 404:
                raise
            self.url = self.add_index_php(self.url)
            self.integration_id.set_settings_value('url', self.url)

        export_images = bool(self.wp_user and self.wp_app_password)
        self.integration_id.allow_export_images = export_images
        self.integration_id.action_active()

        if export_images:
            adapter = self.integration_id.adapter
            endpoint = adapter._get_xmlrpc_endpoint()

            response = XmlRpc.send_request(
                endpoint,
                'wp.getUsersBlogs',
                [self.wp_user, self.wp_app_password],
            )

            if not response.ok:
                raise UserError(f'{response.url}. {response.text}')

            fault = XmlRpc.xml_string_to_dict(response.text, root_tag='fault')
            if fault:
                raise UserError(_('Wrong "WordPress User" or "WordPress Password". Check it.'))

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

        self.env['configuration.wizard.woocommerce.tax.group'].create(values_list)

    def run_after_step_tax_group(self):
        for line in self.configuration_tax_group_ids:
            tax_group = line.external_tax_group_id
            tax_group.default_external_tax_id = line.default_external_tax_id.id
            tax_group.sequence = line.sequence

        return True

    # Step Order Status
    def run_before_step_order_status(self):
        self.integration_id.integrationApiImportSaleOrderStatuses()

    def run_after_step_order_status(self):
        if not self.order_status_ids:
            raise UserError(_('You should select order sub-statuses'))

        ids = [x.code for x in self.order_status_ids]

        receive_filter = self.integration_id.get_class().default_receive_orders_filter
        receive_filter = re.sub('<put state id here>', ','.join(ids), receive_filter)

        self.integration_id.set_settings_value('receive_orders_filter', receive_filter)

        return True

    # Step API
    def run_before_step_api(self):
        api_client = self.integration_id._build_adapter()._client._client

        response = api_client.get(TAX_CLASSES)
        self.api_permissions_read = response.status_code == 200

        response = api_client.post(TAX_CLASSES, {})
        self.api_permissions_write = response.status_code == 400

    def run_after_step_api(self):
        self.run_before_step_api()

        if not(self.api_permissions_read and self.api_permissions_write):
            raise UserError(_('You should grant read and write permissions'))

        return True

    def action_recheck_api(self):
        self.run_before_step_api()

        return self.get_action_view()

    # Step Languages
    def run_before_step_wc_languages(self):
        integration = self.integration_id
        integration.integrationApiImportLanguages()
        shop_env = integration.adapter.get_shop_env()

        default_locale = shop_env['environment']['language']
        code = default_locale.split('_', maxsplit=1)[0]

        lang = self.env['integration.res.lang.external'].search([
            ('code', '=', code),
            ('integration_id', '=', integration.id),
            ('external_reference', '=', default_locale),
        ], limit=1)
        self.language_default_id = lang.id

    def run_after_step_wc_languages(self):
        return self.run_after_step_languages()

    @staticmethod
    def get_form_xml_id():
        return 'integration_woocommerce.view_configuration_wizard'


class QuickConfigurationWooCommerceTaxGroup(models.TransientModel):
    _name = 'configuration.wizard.woocommerce.tax.group'
    _inherit = 'configuration.wizard.tax.group.abstract'
    _description = 'Quick Configuration WooCommerce Tax Group'

    sequence = fields.Integer(
        help=(
            'When exporting from Odoo to WooCommerce, take the most priority item first '
            'in Order to define which Odoo Tax correspond to which tax group.'
        ),
    )
    configuration_wizard_id = fields.Many2one(
        comodel_name='configuration.wizard.woocommerce',
    )
    external_tax_group_id = fields.Many2one(
        string='WooCommerce External Tax Rule',
    )
