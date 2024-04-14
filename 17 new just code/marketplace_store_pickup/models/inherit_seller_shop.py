# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
from odoo import models, fields, tools, api, _
from odoo.exceptions import UserError
from lxml import etree

import requests
import logging
_logger = logging.getLogger(__name__)

ADDRESS_FIELDS = ('street', 'street2', 'zip', 'city', 'state_id', 'country_id')
DAYS = [
    ('monday','Monday'),
    ('tuesday','Tuesday'),
    ('wednesday','Wednesday'),
    ('thusday','Thursday'),
    ('friday','Friday'),
    ('saturday','Saturday'),
    ('sunday','Sunday')
    ]

class SellerShop(models.Model):
    _inherit = 'seller.shop'

    def geo_localize(self):
        geo_obj = self.env['base.geocoder']
        # We need country names in English below
        apikey = self.env['ir.config_parameter'].sudo().get_param('google.api_key_geocode')
        for shop in self.with_context(lang='en_US'):
            search = geo_obj.geo_query_address(
                street=shop.street,
                zip=shop.zip,
                city=shop.city,
                state=shop.state_id.name,
                country=shop.country_id.name
            )
            result = geo_obj.geo_find(search)

            if result is None:
                search = geo_obj.geo_query_address(
                    city=shop.city,
                    state=shop.state_id.name,
                    country=shop.country_id.name
                )
                result = geo_obj.geo_find(search)

            if result:
                shop.write({
                    'store_lat': result[0],
                    'store_long': result[1],
                    'date_localization': fields.Date.context_today(shop)
                })
        return True

    @api.model
    def _get_default_address_format(self):
        return "%(street)s\n%(street2)s\n%(city)s %(state_code)s %(zip)s\n%(country_name)s"

    @api.model
    def _address_fields(self):
        """Returns the list of address fields that are synced from the parent."""
        return list(ADDRESS_FIELDS)

    def _display_address(self, without_company=False):

        '''
        The purpose of this function is to build and return an address formatted accordingly to the
        standards of the country where it belongs.

        :param address: browse record of the res.partner to format
        :returns: the address formatted in a display that fit its country habits (or the default ones
            if not country is specified)
        :rtype: string
        '''
        # get the information that will be injected into the display format
        # get the address format
        address_format = self.country_id.address_format or \
            self._get_default_address_format()
        args = {
            'state_code': self.state_id.code or '',
            'state_name': self.state_id.name or '',
            'country_code': self.country_id.code or '',
            'country_name': self.country_id.name or '',
        }
        for field in self._address_fields():
            args[field] = getattr(self, field) or ''
        if without_company:
            args['company_name'] = ''
        return address_format % args

    def _display_address_depends(self):
        # field dependencies of method _display_address()
        return self._address_fields() + [
            'country_id.address_format', 'country_id.code', 'country_id.name',
            'state_id.code', 'state_id.name',
        ]

    @api.depends(lambda self: self._display_address_depends())
    def _compute_contact_address(self):
        for shop in self:
            shop.contact_address = shop._display_address()

    @api.model
    def set_default_partner(self):
        partner = self.env.user.partner_id
        return partner if partner.seller else False

    coordinate_calc = fields.Selection([('by_addr', 'By Address'),
                                         ('manual', 'Manually')
                                         ], string="Store Co-ordinates", default="by_addr")
    store_lat = fields.Char(string="Store Latitude", digits=(16, 5))
    store_long = fields.Char(string="Store Longitude", digits=(16, 5))
    date_localization = fields.Date(string='Geolocation Date')
    is_globel = fields.Boolean(string="Globel Shop")
    seller_id = fields.Many2one("res.partner", string="Seller", domain="[('seller','=', True)]", required=True, default=set_default_partner)
    seller_product_ids = fields.Many2many("product.template", "shop_product_table", "shop_id", "product_id", string="Products", compute=False)
    shop_location_id = fields.Many2one("stock.location", "Shop Location")
    contact_address = fields.Char(compute='_compute_contact_address', string='Complete Address')
    store_timing = fields.One2many("store.timing", "shop_id", string="Shop Timing")
    available_for_pickup = fields.Boolean("Available For PickUp", help="Enable this to use this shop as a pickup location.")

    _sql_constraints = [('seller_id_uniqe', 'CHECK(1=1)', _('This seller is already assign to another shop.'))]


    def website_publish_button(self):
        for record in self:
            if not record.website_published and len(record.store_timing) != 7:
                raise UserError(_("Please enter store timings for all days."))
        return super(SellerShop, self).website_publish_button()

    def write(self, vals):
        param = ('street', 'street2', 'zip', 'city', 'state_id', 'country_id')
        for rec in self:
            res = super(SellerShop, rec).write(vals)
            if (vals.get('coordinate_calc') == 'by_addr' or rec.coordinate_calc == 'by_addr') and any(key in vals for key in param):
                rec.geo_localize()
            return res

    @api.model
    def create(self, vals):
        param = ('street', 'street2', 'zip', 'city', 'state_id', 'country_id')
        res = super(SellerShop, self).create(vals)
        if res.coordinate_calc == 'by_addr' and any(key in vals for key in param):
            res.geo_localize()
        seller = res.seller_id
        res.shop_location_id = self.env["stock.location"].sudo().create({
            'name': res.name,
            'location_id': seller.get_seller_global_fields('location_id'),
            # 'partner_id': seller.id,
            'usage': 'internal',
        })
        return res

class StoreTiming(models.Model):
    _name = "store.timing"
    _description = "Store Timing"

    shop_id = fields.Many2one("seller.shop", string="Shop")
    days = fields.Selection(selection=DAYS, string="Day", required =True)
    status = fields.Selection(selection=[('open','Open'),('closed','Closed')], default="open", string="Open/Closed Status", required =True)
    open_time = fields.Float(string="Opening Time",required =True)
    close_time = fields.Float(string="Closing Time",required =True)

    def check_time_values(self, vals):
        open_time = vals.get('open_time') if vals.get('open_time') else self.open_time
        close_time = vals.get('close_time') if vals.get('close_time') else self.close_time
        days = vals.get('days') if vals.get('days') else self.days
        shop_id = vals.get('shop_id') if vals.get('shop_id') else self.shop_id.id
        status = vals.get('status') if vals.get('status') else self.status

        if days and shop_id:
            test_slot = self.search([('days','=',days),('shop_id','=',shop_id)])
            if test_slot and test_slot.id != self.id:
                raise UserError(_("There is multiple record of same day."))
        if status == 'open':
            if open_time >= close_time:
                raise UserError(_("Please enter a valid opening and closing time."))
            if open_time >= 24 or open_time < 0:
                raise UserError(_("Please enter a valid hour between 00:00 and 24:00"))
            if close_time >= 24 or close_time < 0:
                raise UserError(_("Please enter a valid hour between 00:00 and 24:00"))

    @api.model
    def create(self, vals):
        self.check_time_values(vals)
        res = super(StoreTiming, self).create(vals)
        return res

    def write(self, vals):
        for rec in self:
            rec.check_time_values(vals)
        res = super(StoreTiming, self).write(vals)
        return res

class Website(models.Model):
    _inherit = 'website'

    @api.model
    def mp_pickup_get_map_api_url(self):
        mp_hyper_module = self.env["ir.module.module"].sudo().search([('state','=','installed'), ('name','=', 'marketplace_hyperlocal_system')])
        if mp_hyper_module:
            return False
        map_api_url = '//maps.googleapis.com/maps/api/js?libraries=places'
        google_maps_api_key = self.env['website'].get_current_website().google_maps_api_key
        if google_maps_api_key:
            map_api_url = '//maps.googleapis.com/maps/api/js?libraries=places&key=' + str(google_maps_api_key)
        return map_api_url
