# Copyright © 2023 Garazd Creation (https://garazd.biz)
# @author: Yurii Razumovskyi (support@garazd.biz)
# @author: Iryna Razumovska (support@garazd.biz)
# License OPL-1 (https://www.odoo.com/documentation/15.0/legal/licenses.html).

from typing import Dict, List

from odoo import _, api, fields, models


class WebsiteTrackingService(models.Model):
    _name = "website.tracking.service"
    _inherit = ['mail.thread']
    _description = 'Service that gets Tracking Event Data'
    _order = 'sequence, website_id, type'

    def _default_website(self):
        return self.env['website'].search([('company_id', '=', self.env.company.id)], limit=1)  # flake8: noqa: E501

    # flake8: noqa: E501
    type = fields.Selection(selection=[])
    key = fields.Char(tracking=True)
    key_is_required = fields.Boolean(default=True, tracking=True)
    cookie_type = fields.Selection(selection=[])
    website_id = fields.Many2one(
        comodel_name='website',
        ondelete='cascade',
        default=_default_website,
        required=True,
    )
    item_type = fields.Selection(
        selection=[
            ('product.template', 'Product Template ID'),
            ('product.product', 'Product ID'),
        ],
        default='product.template',
        required=True,
    )
    category_type = fields.Selection(
        selection=[
            ('public', 'Public Category (with hierarchy)'),
            ('product', 'Product Category'),
        ],
        default='public',
        required=True,
    )
    is_internal_logged = fields.Boolean(string="Internal Logs", tracking=True)
    sequence = fields.Integer(default=100)
    active = fields.Boolean(default=True, tracking=True)
    # Advanced Matching
    privacy_url = fields.Char(string='Data Use Privacy URL', readonly=True)
    track_id_external = fields.Boolean(string="Track External ID", tracking=True)
    track_ip_address = fields.Boolean(string="Track IP Address", tracking=True)
    track_user_agent = fields.Boolean(tracking=True)
    track_email = fields.Boolean(tracking=True)
    track_phone = fields.Boolean(tracking=True)
    track_country = fields.Boolean(tracking=True)
    track_city = fields.Boolean(tracking=True)
    track_customer_data_source = fields.Selection(
        selection=[
            ('visitor', 'Website Visitor'),
            ('sale_order', 'Sale Order Partner'),
        ],
        string='Customer Data Source',
        default='visitor',
        tracking=True,
    )
    lead_value = fields.Float(default=1.0, help="A lead value for the Contact Us form.")
    show_lead_value = fields.Boolean(compute='_compute_show_lead_value')

    @api.constrains('type', 'track_id_external', 'track_ip_address', 'track_user_agent',
                    'track_email', 'track_phone', 'track_country', 'track_city')
    def _check_available_visitor_data(self):
        """Define what website visitor data can be activated in a service.
        Method to override."""
        # pylint: disable-msg=unnecessary-pass
        pass

    @api.depends('type')
    def _compute_show_lead_value(self):
        for service in self:
            service.show_lead_value = 'lead' in self.env['website']._tracking_event_mapping(service.type).keys()

    @api.depends('type', 'key')
    def _compute_display_name(self):
        for service in self:
            service.display_name = "%s%s" % (
                dict(self._fields['type'].selection).get(service.type),
                service.key and f": {service.key}" or ''
            )

    def allow_send_data(self):
        """Method to check additional restrictions. To override."""
        self.ensure_one()
        return self.active and self.key

    def get_item(self, item_data):
        self.ensure_one()
        service = self
        template_id = item_data.get('product_tmpl_id')
        variant_id = item_data.get('product_id')
        if service.item_type == 'product.template':
            product = self.env['product.template'].browse(template_id)
        elif service.item_type == 'product.product':
            product = self.env['product.product'].browse(variant_id)
        else:
            product = None
        return product

    def get_item_categories(self, product, property_name: str = 'content_category') -> Dict:
        """Generate a product category hierarchy structure.
        :param product: a record of the "product.product" model
        """
        self.ensure_one()
        res = {}
        if self.category_type == 'product':
            res.update({property_name: product.categ_id.name})
        elif self.category_type == 'public':
            # Use the first public category of a product
            if product.public_categ_ids[:1]:
                category = product.public_categ_ids[:1].name
            else:
                category = _('All products')
            res.update({property_name: category})
        return res

    def get_common_data(self, event_type, product_data_list=None, order=None, pricelist=None):
        self.ensure_one()
        return {}

    def get_item_data_from_product_list(self, product_data_list, pricelist) -> Dict:
        """Prepare data for a tracking service from a product data list.
        :param product_data_list: a list with product data (take a look at "controllers/main.py")
        :param pricelist: a record of the model "product.pricelist"
        """
        self.ensure_one()
        return {}

    def get_item_data_from_order(self, order) -> Dict:
        """Prepare data for a tracking service from a sale order.
        :param order: a record of the model "sale.order"
        """
        self.ensure_one()
        return {}

    def _get_final_product_price(self, order_line) -> float:
        self.ensure_one()
        if self.env.user.has_group('account.group_show_line_subtotals_tax_excluded'):
            price = order_line.price_reduce_taxexcl
        elif self.env.user.has_group('account.group_show_line_subtotals_tax_included'):
            price = order_line.price_reduce_taxinc
        else:
            price = order_line.price_unit
        return price

    def get_data_for_lead(self, product_data_list=None, pricelist=None, order=None):
        self.ensure_one()
        return {'value': self.lead_value}

    def get_data_for_login(self, product_data_list=None, pricelist=None, order=None):
        self.ensure_one()
        return {}

    def get_data_for_sign_up(self, product_data_list=None, pricelist=None, order=None):
        self.ensure_one()
        return {}

    def get_data_for_view_product_list(self, product_data_list=None, pricelist=None, order=None):
        self.ensure_one()
        return self.get_item_data_from_product_list(product_data_list, pricelist)

    def get_data_for_view_product_category(self, product_data_list=None, pricelist=None, order=None):
        self.ensure_one()
        return self.get_item_data_from_product_list(product_data_list, pricelist)

    def get_data_for_search_product(self, product_data_list=None, pricelist=None, order=None):
        self.ensure_one()
        return self.get_item_data_from_product_list(product_data_list, pricelist)

    def get_data_for_view_product(self, product_data_list=None, pricelist=None, order=None):
        self.ensure_one()
        return self.get_item_data_from_product_list(product_data_list, pricelist)

    def get_data_for_add_to_wishlist(self, product_data_list=None, pricelist=None, order=None):
        self.ensure_one()
        return self.get_item_data_from_product_list(product_data_list, pricelist)

    def get_data_for_add_to_cart(self, product_data_list=None, pricelist=None, order=None):
        self.ensure_one()
        return self.get_item_data_from_product_list(product_data_list, pricelist)

    def get_data_for_begin_checkout(self, product_data_list=None, pricelist=None, order=None):
        self.ensure_one()
        return self.get_item_data_from_order(order)

    def get_data_for_add_shipping_info(self, product_data_list=None, pricelist=None, order=None):
        self.ensure_one()
        return self.get_item_data_from_order(order)

    def get_data_for_add_payment_info(self, product_data_list=None, pricelist=None, order=None):
        self.ensure_one()
        return self.get_item_data_from_order(order)

    def get_data_for_purchase(self, product_data_list=None, pricelist=None, order=None):
        self.ensure_one()
        return self.get_item_data_from_order(order)

    def get_data_for_purchase_portal(self, product_data_list=None, pricelist=None, order=None):
        self.ensure_one()
        return self.get_item_data_from_order(order)

    @api.model
    def _visitor_data_mapping(self, service_type: str):
        """Return dictionary with mappings of visitor data params
        for specific type of tracking service. Method to override."""
        return {
            'external_ref': {'name': 'external_ref', 'hash': True},
            'first_name': {'name': 'first_name', 'hash': True},
            'last_name': {'name': 'last_name', 'hash': True},
            'email': {'name': 'email', 'hash': True},
            'phone':  {'name': 'phone', 'hash': True, 'remove_plus': False},
            'country':  {'name': 'country', 'hash': True},
            'city':  {'name': 'city', 'hash': True},
            'zip':  {'name': 'zip', 'hash': True},
            'state':  {'name': 'state', 'hash': True},
            'ip_address':  {'name': 'ip_address', 'hash': False},
            'user_agent':  {'name': 'user_agent', 'hash': False},
        }

    # pylint: disable-msg=too-many-locals,too-many-branches,too-many-statements
    def get_visitor_data(self, visitor_id: int = None, sale_order_id: int = None) -> Dict:
        self.ensure_one()
        visitor_data = {}
        # flake8: noqa: E501

        # Get customer data from a sale order in priority if this option is checked
        sale_order = self.env['sale.order'].sudo().browse(sale_order_id) if sale_order_id else None
        if sale_order and self.track_customer_data_source == 'sale_order' and sale_order.partner_id != self.env.ref('base.public_partner'):
            partner = sale_order.partner_id
            external_ref = str(partner.id)
            email = partner.email
            country = partner.country_id
            phone = partner.phone or partner.mobile

        # Otherwise, get customer data from a visitor
        else:
            if not visitor_id:
                visitor = self.env['website.visitor']._get_visitor_from_request(force_create=False)
            else:
                visitor = self.env['website.visitor'].sudo().browse(visitor_id)
            if not visitor:
                return visitor_data

            partner = visitor.partner_id
            external_ref = visitor.access_token
            email = visitor.email
            country = partner.country_id or visitor.country_id
            phone = partner and (partner.phone or partner.mobile) or visitor.mobile

        service = self
        log = self.env['website.tracking.log']
        mapping = self._visitor_data_mapping(service.type)

        if service.track_id_external and external_ref:
            mapping_external_ref = mapping["external_ref"]
            visitor_data[mapping_external_ref['name']] = log._hash_sha256(external_ref) if mapping_external_ref["hash"] else external_ref

        if service.track_country and country:
            mapping_country = mapping["country"]
            visitor_data[mapping_country["name"]] = log._hash_sha256(country.name) if mapping_country["hash"] else country.name

        if service.track_city and partner.city:
            mapping_city = mapping["city"]
            visitor_data[mapping_city["name"]] = log._hash_sha256(partner.city) if mapping_city["hash"] else partner.city

        if service.track_email and email:
            mapping_email = mapping["email"]
            res = log._hash_email(email) if mapping_email["hash"] else email
            if mapping_email.get('type') and mapping_email.get('type') == 'list':
                res = [res]
            visitor_data[mapping_email["name"]] = res

        if service.track_phone and phone and country:
            mapping_phone = mapping["phone"]
            phone_number = log._format_phone_number(phone, country, remove_plus=mapping_phone.get('remove_plus', False))
            visitor_data[mapping_phone["name"]] = log._hash_sha256(phone_number) if mapping_phone["hash"] else phone_number

        request_data = self._context.get('request_data', {})
        if request_data:
            ip_address = request_data.get('ip')
            if service.track_ip_address and ip_address:
                mapping_ip_address = mapping["ip_address"]
                visitor_data[mapping_ip_address["name"]] = log._hash_sha256(ip_address) if mapping_ip_address["hash"] else ip_address

            user_agent = request_data.get('user_agent')
            if service.track_user_agent and user_agent:
                mapping_user_agent = mapping["user_agent"]
                visitor_data[mapping_user_agent["name"]] = log._hash_sha256(user_agent) if mapping_user_agent["hash"] else user_agent

        return visitor_data

    @api.model
    def _get_privacy_url(self) -> Dict:
        return {}

    @api.model
    def _fields_to_invalidate_cache(self) -> List[str]:
        return ['sequence', 'website_id', 'key', 'active']

    @api.model_create_multi
    def create(self, vals_list):
        # Set up a default privacy URL for a tracking services
        for vals in vals_list:
            service_type = vals.get('type')
            if service_type and self._get_privacy_url().get(service_type):
                vals['privacy_url'] = self._get_privacy_url().get(service_type)
        record = super(WebsiteTrackingService, self).create(vals_list)
        # Invalidate the caches to apply changes on webpages
        self.env.registry.clear_cache()
        return record

    def write(self, vals):
        result = super(WebsiteTrackingService, self).write(vals)
        if any(fld in vals for fld in self._fields_to_invalidate_cache()):
            # Invalidate the caches to apply changes on webpages
            self.env.registry.clear_cache()
        return result

    def extra_log_data(self):
        """Add extra values on to the "log" record. Method to override."""
        self.ensure_one()
        return {}

    def post_processed_data(self, event_data: Dict) -> Dict:
        """Perform post-processing of event data. Return a dictionary to update.
           Method to override.
        """
        self.ensure_one()
        return {}
