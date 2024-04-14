# -*- coding: utf-8 -*-
##########################################################################
# Author : Webkul Software Pvt. Ltd. (<https://webkul.com/>;)
# Copyright(c): 2017-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>;
##########################################################################

# Python Module
import pytz
import requests
import json
import logging
from datetime import datetime, timedelta
from ast import literal_eval
from markupsafe import Markup

# Odoo Module
from odoo.tools.mimetypes import guess_mimetype
from odoo.http import request
from odoo.exceptions import UserError, ValidationError
from odoo.addons.http_routing.models.ir_http import slug
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)
UTC = pytz.utc


JUNKMAPPING = []
BATCHAPI = "https://shoppingcontent.googleapis.com/content/v2.1/products/batch"
AUTHAPI = "https://www.googleapis.com/content/v2.1/"


class GoogleMerchantShop(models.Model):
    _name = 'google.shop'
    _inherit = ["mail.thread"]
    _description = 'Shop for performing operation on products for merchant center'
    name = fields.Char(string="Name", required=True)

    # === Default Method ===#

    def _default_website(self):
        return self.env['website'].get_current_website()

    def _default_pricelist(self):
        return self.env['website'].get_current_website()._get_current_pricelist()
    
    def _default_field_mapping(self):
        return self.env['field.mapping'].search([('active', '=', True)], limit=1)

    # -------------------------------------------------------------------------//
    # MODEL FIELDS
    # -------------------------------------------------------------------------//
    domain_input = fields.Char(string="Domain", default="[]")
    limit = fields.Integer(string="Limit", default=10)

    channel = fields.Selection([("online", "Online"), ("local", "Local")], string="Channel",
                               required=True, help="Select that whether your store is Online or Offline")
    product_selection_type = fields.Selection([('domain', 'Domain'), ('manual', 'Manual')], default="domain",
                                              string="Product Select Way", help="Select whether you want to select the product manually or with the help of domain")
    merchant_id = fields.Char(name="Merchant Id", help="Merchant Id of your merchant account",
                              related="oauth_id.merchant_id", readonly=True)
    shop_status = fields.Selection(
        [('new', 'New'), ('validate', 'Validate'), ('error', 'Error'), ('done', 'Done')], default='new')
    currency_id = fields.Many2one(
        string="Currency", store=True, related="product_pricelist_id.currency_id")
    website_id = fields.Many2one(
        'website', string="website", default=_default_website)

    oauth_id = fields.Many2one(string="Account", comodel_name="oauth2.detail", required=True,
                               help="Select the account with which you want to sync the products")
    content_language = fields.Many2one(string="Content Language", comodel_name="res.lang",
                                       required=True, help="Language in which your products will get sync on Google Shop")
    target_country = fields.Many2one(string="Target Country", comodel_name="res.country",
                                     required=True, help="Select the country in which you want to sell the products")
    product_pricelist_id = fields.Many2one(comodel_name="product.pricelist", string="Product Pricelist", required=True,
                                           help="select the pricelist according to which your product price will get selected", default=_default_pricelist)
    field_mapping_id = fields.Many2one(comodel_name="field.mapping", string="Field Mapping", domain=[
                                       ('active', '=', True)], required=True, default=_default_field_mapping)
    product_ids_rel = fields.Many2many(comodel_name='product.product', relation='merchant_shop_product_rel', column1='google_id', column2='product_id', domain=[
                                       ("sale_ok", "=", True), ("website_published", "=", True)], string="Products")
    shop_url = fields.Char(name="Shop URL", help="Write your domain name of your website",
                           related="oauth_id.domain_url", readonly=True)
    mapping_count = fields.Integer(
        string="Total Mappings", compute="_mapping_count")
    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Name should be Unique')]

    def _get_product_domain(self):
        f_domain = [("sale_ok", "=", True), ("website_published", "=",
                                             True), ('website_id', 'in', (self.website_id.id, False))]
        return f_domain
    
    def reset_state(self):
        for rec in self:
            rec.shop_status = 'new'

    def error_log(self, message, content):
        _logger.info(" <<  {}  >>{}".format(message, content))

    def manage_error_products(self):
        error_state_records = self.env['product.mapping'].search(
            [('product_status', '=', 'error'), ('google_shop_id', '=', self.id)])
        done_state_records_product = self.env['product.mapping'].search(
            [('product_status', '=', 'updated'), ('google_shop_id', '=', self.id)]).mapped('product_id').ids
        if error_state_records:
            for record in error_state_records:
                if record.product_id.id in done_state_records_product:
                    record.unlink()

    def product_ids_domain_or_manual(self, mapped_products_product_ids, error_products_product_ids):
        if (self.product_selection_type == 'domain'):
            try:
                fixed_domain = self._get_product_domain(
                ) + [('id', 'not in', mapped_products_product_ids)]
                limit = self.limit-len(error_products_product_ids) if (
                    self.limit-len(error_products_product_ids)) > 0 else 0
                if self.domain_input:
                    final_domain = literal_eval(
                        self.domain_input) + fixed_domain
                else:
                    final_domain = fixed_domain
                if limit == 0:
                    product_ids = []
                else:
                    product_ids = self.env["product.product"].search(
                        final_domain, limit=limit).ids
            except:
                return self.env['wk.wizard.message'].genrated_message("Enter Domain Properly", name='Message')
        else:
            product_ids = self.product_ids_rel.ids
        return product_ids

    def _manage_product_for_api(self, all_products_to_be_upload, context, updation_type):
        total_product = 0
        done_count = 0
        error_msg = ''
        batch_of_all_products = {}
        total_no_of_products = len(all_products_to_be_upload)
        while total_no_of_products > 0:
            if total_no_of_products > 1000:
                product_to_update = all_products_to_be_upload[:1000]
                batch_of_all_products["entries"] = product_to_update
                all_products_to_be_upload = all_products_to_be_upload[1000:]
                total_no_of_products = len(
                    all_products_to_be_upload)
            else:
                batch_of_all_products["entries"] = all_products_to_be_upload
                total_no_of_products = 0
            response = self.with_context(
                context).call_google_insert_api(batch_of_all_products)
            if response.status_code != 200:
                response_content = literal_eval(response.text)
                message = response_content.get("error")
                self.error_log("Export Response Error", message)
                return self.env['wk.wizard.message'].genrated_message(message, name='Message')

            if updation_type == "update":
                total_product, done_count, error_msg = self.manage_update_response_of_api(
                    response, total_product, done_count)
                if error_msg:
                    return error_msg
            else:
                total_product, done_count, error_msg = self.manage_insert_response_of_api(
                    response, total_product, done_count)
                if error_msg:
                    return error_msg
        if updation_type == "update":
            message = ("<b>{0} out of {1}</b> products are updated: We're on a roll!".format(
                done_count, total_product))
        else:
            message = ("Looks like our data export machine is as reliable as an octopus trying to play the piano - <b>{0} out of {1}</b> products made it safely to their destination!".format(
                done_count, total_product))
            self.manage_error_products()
            if done_count == total_product:
                self.shop_status = "done"
        return self.env['wk.wizard.message'].genrated_message(message, name='Message')

    def manage_insert_response_of_api(self, response, total_product, done_count):

        call_response = response.json()
        error_msg = ''
        if response.status_code == 401:
            self.shop_status = "error"
            message = "Account ID might had been expired so, refresh it and try again"
            raise UserError(_(message))
        elif response.status_code == 200:
            if 'entries' in call_response.keys():
                all_products_response = call_response['entries']
                for response in all_products_response:
                    total_product += 1
                    if 'kind' and 'batchID' and 'product' in response.keys():
                        update_status = True
                        product_status = 'updated'
                        msg = "Product is exported Successfully"
                        google_product_ids = response['product']['id']
                    else:
                        update_status = False
                        product_status = 'error'
                        msg = response['errors']['message']
                        google_product_ids = None
                    if response['batchId'] in JUNKMAPPING:
                        self.env['product.mapping'].search([('product_id','=', response['batchId'])], limit=1).write({
                            'update_status': update_status,
                            'product_status': product_status,
                            'message': msg,
                            'google_product_id': google_product_ids})
                    else:
                        self.env['product.mapping'].create({
                            'google_shop_id': self.id,
                            'product_id': response['batchId'],
                            'update_status': update_status,
                            'product_status': product_status,
                            'message': msg,
                            'google_product_id': google_product_ids})
                    if update_status:
                        done_count += 1
            else:
                self.shop_status = "done"
                message = "Well, it seems like your data is on vacation in the Land of Nowhere and having a grand old time sunbathing on the beaches of <b>No Information Island! </b>"
                return (0, 0, self.env['wk.wizard.message'].genrated_message(message, name="Export Alert: Oops, we're empty-handed!"))
        else:
            self.shop_status = "error"
            message = call_response['error']['message']
            raise UserError(_(message))
        return (total_product, done_count, error_msg)

    def button_export_product(self):
        token_result = self.oauth_id.button_get_token(self.oauth_id)
        if token_result == "error":
            return self.env['wk.wizard.message'].genrated_message("Attention, Captain! Your account needs a high-five from the authorization fairy before setting sail into the digital seas.\n Get ready to unlock the magic!", name='Authorization Request')
        updation_type = "export"
        all_products_to_be_upload = []
        field_mapping_lines = self.field_mapping_id.field_mapping_line_ids
        mapped_product_details = self.env['product.mapping'].search(
            [('google_shop_id', '=', self.id)])
        error_product_details = mapped_product_details.filtered(
            lambda r: r.product_status == "error")
        error_products_product_ids = error_product_details.mapped(
            'product_id').ids
        mapped_products_product_ids = mapped_product_details.mapped(
            'product_id').ids
        error_products_mapped_ids = [(x.id, x.product_id.id)
                                     for x in error_product_details]
        JUNKMAPPING.extend(error_products_product_ids)
        product_ids = self.product_ids_domain_or_manual(
            mapped_products_product_ids, error_products_product_ids)
        context = self._context.copy()
        context.update({'lang': self.content_language.code,
                       'pricelist': self.product_pricelist_id.id, 'website_id': self.website_id.id, 'url_code': self.content_language.url_code or self._default_website().default_lang_id.url_code})
        ids_to_export = list(set(product_ids)-set(mapped_products_product_ids))
        product_detail = self.with_context(context).get_product_detail(
            field_mapping_lines.ids, ids=ids_to_export)
        error_product_detail = self.with_context(context).get_product_detail(
            field_mapping_lines.ids, ids=error_products_product_ids)
        error_product_shop_link = []
        if error_product_detail:
            error_product_shop_link = [
                y for x in error_products_mapped_ids for y in error_product_detail if (x[1] == y.get('id'))]
            product_detail += error_product_shop_link
        if len(ids_to_export) == 0 and len(error_product_shop_link) == 0:
            self.shop_status = "done"
            message = "Well, it seems like your data is on vacation in the Land of Nowhere and having a grand old time sunbathing on the beaches of<b> No Information Island! </b>"
            return self.env['wk.wizard.message'].genrated_message(message, name="Export Alert: Oops, we're empty-handed!")
        base_url = self.shop_url or self.env['ir.config_parameter'].sudo(
        ).get_param('web.base.url')
        all_products_to_be_upload.extend(self.with_context(context).get_mapped_set(
            product_detail, field_mapping_lines, base_url=base_url, operation='insert'))
        self.oauth_id.button_get_token(self.oauth_id)
        return self._manage_product_for_api(all_products_to_be_upload, context, updation_type)

    def manage_update_response_of_api(self, response, total_product, done_count):
        call_response = response.json()
        error_msg = ''
        if response.status_code == 401:
            self.shop_status = "error"
            message = "Account ID might had been expired so, refresh it and try again"
            raise UserError(_(message))
        elif response.status_code == 200:
            if 'entries' in call_response.keys():
                all_products_response = call_response['entries']
                for response in all_products_response:
                    total_product += 1
                    if 'kind' and 'batchID' and 'product' in response.keys():
                        self.env['product.mapping'].search([('google_product_id', '=', response['product']['id']), ('google_shop_id', '=', self.id)]).write({
                            'update_status': True,
                            'product_status': 'updated',
                            'message': "Product id updated Successfully",
                            'google_product_id': response['product']['id']})
                        done_count += 1
                    else:
                        self.shop_status = "error"
                        self.env['product.mapping'].search([('product_id.id', '=', response['batchId']), ('google_shop_id', '=', self.id)]).write({
                            'update_status': False,
                            'product_status': 'error',
                            'message': response['errors']['message'],
                            'google_product_id': None})
            else:
                self.shop_status = "done"
                message = "Our data elves searched high and low but <b>found no changes</b> to sprinkle their upgrade magic on. It's a quiet day in the land of updates!"
                return (0, 0, self.env['wk.wizard.message'].genrated_message(message, name='Update Alert!'))
        else:
            self.shop_status = "error"
            message = call_response['error']['message']
            raise UserError(_(message))
        return (total_product, done_count, error_msg)

    def button_update_product(self, update_all_product=False):
        updation_type = "update"
        all_products_to_be_upload = []
        if update_all_product:
            updated_fields = self.env['product.mapping'].search(
                [('google_shop_id', '=', self.id), ('product_status', '=', 'updated')])
            operation_type = 'insert'
        else:
            token_result = self.oauth_id.button_get_token(self.oauth_id)
            if token_result == "error":
                return self.env['wk.wizard.message'].genrated_message("Attention, Captain! Your account needs a high-five from the authorization fairy before setting sail into the digital seas. \n Get ready to unlock the magic!", name='Authorization Request')
            updated_fields = self.env['product.mapping'].search([('google_shop_id', '=', self.id), (
                'update_status', '=', False), ('product_status', '=', 'updated')], limit=self.limit)
            operation_type = 'update'
        context = self._context.copy()
        context.update({'lang': self.content_language.code,
                       'pricelist_id': self.product_pricelist_id.id, 'website_id': self.website_id.id, 'url_code': self.content_language.url_code or self._default_website().default_lang_id.url_code})
        field_mapping_lines = self.field_mapping_id.field_mapping_line_ids
        updated_products_product_ids = updated_fields.mapped('product_id').ids
        updated_products_mapped_ids = [
            (x.id, x.product_id.id) for x in updated_fields]
        updated_product_detail = self.with_context(context).get_product_detail(
            field_mapping_lines.ids, ids=updated_products_product_ids)
        updated_product_shop_link = [
            y for x in updated_products_mapped_ids for y in updated_product_detail if (x[1] == y.get('id'))]
        if len(updated_product_shop_link) == 0:
            self.shop_status = "done"
            message = "Our data elves searched high and low but <b>found no changes</b> to sprinkle their upgrade magic on. It's a quiet day in the land of updates!"
            return self.env['wk.wizard.message'].genrated_message(message, name='Update Alert!')
        base_url = self.shop_url or self.env['ir.config_parameter'].sudo(
        ).get_param('web.base.url')
        all_products_to_be_upload.extend(self.with_context(context).get_mapped_set(
            updated_product_shop_link, field_mapping_lines, base_url=base_url, operation=operation_type))
        return self._manage_product_for_api(all_products_to_be_upload, context, updation_type)

    def get_product_detail(self, field_mapping_lines_ids, ids=[]):
        """
        !!!! -------- All the query that are excuted executes here only
        """
        if not ids:
            return []
        field_mapping_model_ids = self.env['field.mapping.line'].search(
            [('id', 'in', field_mapping_lines_ids), ('fixed', '=', False)]).mapped('model_field_id').ids
        field_mapping_model_name = self.env['ir.model.fields'].search(
            [('id', 'in', field_mapping_model_ids)]).mapped("name")
        field_mapping_model_name.append('product_tmpl_id')
        context = self._context.copy()
        context.update({'pricelist': self.product_pricelist_id.id,
                       'website_id': self.website_id.id})
        product_detail = self.env['product.product'].with_context(
            context).search_read([('id', 'in', ids)], field_mapping_model_name)
        return product_detail

    def call_google_insert_api(self, post_dict={}):
        if (self.oauth_id.authentication_state == 'authorize_token'):
            api_call_headers = {'Authorization': "Bearer " +
                                self.oauth_id.access_token, 'Content-Type': 'application/json'}
            api_call_response = requests.post(BATCHAPI,
                                              headers=api_call_headers, data=json.dumps(post_dict), verify=True, timeout=30)
            return api_call_response

    def get_mapped_set(self, product_set, field_mapping_lines, base_url, operation):
        prod_temp_ref = self.env['product.template']
        product_batch_data_list = []
        for product_detail in product_set:
            product = {}
            # available_qty=product_detail.get('qty_available',1)
            if operation == 'insert':
                product_batch_data = {
                    "method": "insert",
                    'product': {}
                }
                product['targetCountry'] = self.target_country.code
                product['channel'] = self.channel
                product['contentLanguage'] = self.content_language.iso_code.split("_")[
                    0]
            else:
                product_batch_data = {
                    "method": "update",
                    'product': {}
                }
                product_id = self.env['product.mapping'].search(
                    [('product_id.id', '=', product_detail.get('id')), ('google_shop_id', '=', self.id)])
                product_batch_data['productId'] = product_id[0].google_product_id
            product_batch_data['merchantId'] = self.merchant_id
            product_batch_data['batchId'] = product_detail.get('id')
            # product['ID'] = str(product_detail.get('id'))
            product_id = self.env['product.product'].sudo().browse(
                product_detail.get('id'))
            if product_id.is_published:
                datetime_utc = datetime.now(UTC)+timedelta(days=30)
                product['expiration_date'] = datetime_utc.strftime(
                    '%Y-%m-%dT%H:%M%z')
            else:
                datetime_utc = datetime.now(UTC)
                product['expiration_date'] = datetime_utc.strftime(
                    '%Y-%m-%dT%H:%M%z')
            product_record = self.env['product.product'].search(
                [('id', '=', product_detail.get('id'))])
            product['imageLink'] = "%s/web/image/product.product/%s/image_1024" % (
                base_url, product_detail.get('id'))
            product['link'] = base_url+'/'+self._context.get('url_code', 'en')+"/shop/product/"+slug(
                prod_temp_ref.search([('id', '=', product_id.product_tmpl_id.id)], limit=1))
            pricelist = self.product_pricelist_id

            # Pricelist price doesn't have to be converted
            pricelist_price = pricelist._get_product_price(     #saleprice
                product=product_id,
                quantity=1,
                target_currency=product_id.currency_id,
            )
            product_price = product_detail.get('price')
            price_dict = {}
            for line in field_mapping_lines:
                key = line.google_field_id.name
                if key in ['link', 'imageLink'] or (operation == 'update' and key in ['offerId', 'id']):
                    continue
                if line.fixed:
                    product[key] = line.fixed_text

                elif line.is_a_attribute:
                    if product_id.product_template_attribute_value_ids:
                        for attr in product_id.product_template_attribute_value_ids:
                            if attr.attribute_id.id == line.attribute_id.id:
                                if key == "sizes":
                                    product[key] = [attr.name]
                                else:
                                    product[key] = attr.name
                                break

                else:
                    # ---------------make value accorrding to fixed layout
                    if (key in ['salePrice','price']):
                        val = product_detail.get(line.model_field_id.name)
                        if key == 'price':
                            if not isinstance(val,bool) and (isinstance(val,int) or isinstance(val,float)):
                                salePrice_val = product.get('salePrice', False)
                                if salePrice_val:
                                    price_value = salePrice_val.get('value',0)
                                    if salePrice_val.get('value',0) > val:
                                        salePrice_val.update({'value':val})
                                        price_dict = dict(value=price_value,currency=self.currency_id.name)
                                        product['salePrice'] = salePrice_val
                                    else:
                                        price_dict = dict(value=val,currency=self.currency_id.name)
                                else:
                                    price_dict = dict(value=val,currency=self.currency_id.name)
                            else:
                                raise UserError("Add price field mapping with a integer or float type field.")
                        else:
                            # Here, our assumption is that the list price field will consistently correspond to the sale price field.
                            val = pricelist_price if line.model_field_id.name == "list_price" else val 
                            if not isinstance(val,bool) and (isinstance(val,int) or isinstance(val,float)):
                                product_price = price_dict.get('value', False)
                                if product_price and val > product_price:
                                    price_dict = dict(value=val,currency=self.currency_id.name)
                                    product[key] = dict(value=product_price,currency=self.currency_id.name)
                                else:
                                    price_dict = dict(value=val,currency=self.currency_id.name)
                                    product[key] = dict(value=val,currency=self.currency_id.name)
                            else:
                                raise UserError("Add salePrice field mapping with a integer or float type field.")

                        # tz=datetime.now(pytz.timezone(self.env.context.get('tz'))).strftime('%z')
                        # product['salePriceEffectiveDate']= '2022-03-20T13:00'+tz+'/ 2022-03-29T15:30'+tz
                    # elif (key=='availability'):
                    #     if available_qty and available_qty>0:
                    #         product['availability']='in_stock'
                    #     else:
                    #         product['availability']='out_of_stock'
                    else:
                        val = product_detail.get(line.model_field_id.name)
                        if line.model_field_id.ttype in ["selection"] and key != 'googleProductCategory':
                            val = dict(prod_temp_ref._fields[line.model_field_id.name].selection).get(
                                product_id.mapped(line.model_field_id.name)[0])
                        elif key == 'googleProductCategory':
                            val = int(product_detail.get(
                                line.model_field_id.name)) if line.model_field_id.name == 'google_shop_product_categ' else False
                        elif line.model_field_id.ttype in ["many2one"]:
                            val = val[1] if val else False
                        if val or line.default:
                            product[key] = val or line.default
            if not price_dict.get('value',False):
                price = product_price if pricelist_price < product_price else pricelist_price
                price_dict = dict(
                    value = self._calculate_tax_included_price(product_id, price),
                    currency=self.currency_id.name
                )
            else:
                price_value = price_dict.get('value')
                tax_included_price = self._calculate_tax_included_price(product_id, price_value)
                price_dict.update({'value': tax_included_price})
            
            # Tax include Hook
            if product.get('salePrice', False):
                s_price_dict = product.get('salePrice')
                price_value = s_price_dict.get('value')
                tax_included_price = self._calculate_tax_included_price(product_id, price_value)
                product.get('salePrice').update({'value': tax_included_price})

            product['price'] = price_dict
            product_batch_data.update({'product': product})
            
            product_batch_data_list.append(product_batch_data)
        return product_batch_data_list
    
    def _calculate_tax_included_price(self, product_id, price):
        return product_id.product_tmpl_id.taxes_id.compute_all(price, product=product_id.product_tmpl_id, partner=self.env['res.partner']).get('total_included')

    def button_authorize_merchant(self):
        if self.merchant_id:
            api_call_response = {}
            token_result = self.oauth_id.button_get_token(self.oauth_id)
            if token_result == "error":
                return self.env['wk.wizard.message'].genrated_message("Please check authorize your account...", name='Message')
            try:
                api_call_headers = {
                    'Authorization': "Bearer "+self.oauth_id.access_token}
                api_call_response = requests.get(AUTHAPI+self.merchant_id +
                                                 '/accounts/'+self.merchant_id, headers=api_call_headers, verify=True, timeout=30)       
                _logger.info(
                    "Response status of the Auth Token and Merchant ID :- %r", api_call_response.status_code)
                
                response_dict = json.loads(api_call_response.text)
                if api_call_response.status_code != 200:
                    message = response_dict.get("error",False)
                    self.error_log("Authentication Error", message)
                    return self.env['wk.wizard.message'].genrated_message(message, name='Message')
                else:
                    self.shop_status = 'validate'
            except:
                message = "Please Go to Account in setting and generate account token first"
                return self.env['wk.wizard.message'].genrated_message(message, name='Message')
        else:
            raise UserError(
                "Please enter the merchant ID in the account Section first")

    @api.constrains('channel', 'target_country', 'content_language')
    def _criteria(self):
        for record in self:
            same_record = record.search(
                ['&', '&',
                    ('channel', '=', record.channel),
                    ('target_country', '=', record.target_country.id),
                    ('content_language', '=', record.content_language.id)
                 ]
            ).ids

            if len(same_record) > 1:
                raise ValidationError(_('Same Shop Exists in Database'))

    # -------------------------------------------------------------------------
    # TOKEN STATUS
    # -------------------------------------------------------------------------
    def get_token_status(self):
        return self.oauth_id.button_get_token(self.oauth_id)

    def open_product_mapping_view(self):
        mappings = self.env['product.mapping'].search(
            [('google_shop_id', '=', self.id)]).ids
        action = self.env.ref(
            'google_shop.product_mapping_action_button_click').read()[0]
        action['domain'] = [('id', 'in', mappings)]
        return action

    def unlink(self):
        for rec in self:
            if rec.mapping_count <= 0:
                super(GoogleMerchantShop, rec).unlink()
            else:
                raise UserError(
                    "Firstly Delete all the mappings then the shop will be deleted")

    def _mapping_count(self):
        for rec in self:
            rec.mapping_count = self.env['product.mapping'].search_count(
                [('google_shop_id', '=', rec.id)])

    def button_delete_product_link(self):
        oauth2_error, error_count, done_count = 0, 0, 0

        mapping_ref = self.env['product.mapping'].search(
            [('google_shop_id', '=', self.id)])

        if len(mapping_ref) == 0:
            self.shop_status = "done"
            message = "Well, it's like searching for a unicorn in a haystack - there's nothing to delete here, just some top-secret records of our covert pancake-flipping operations! "
            return self.env['wk.wizard.message'].genrated_message(message, name='Mission Impossible!')

        if mapping_ref:
            oauth2_error, error_count, done_count = mapping_ref.unlink()

        elif oauth2_error > 0:
            self.shop_status = "error"
            message = "Account ID might had been expired so, refresh it and try again"
            return self.env['wk.wizard.message'].genrated_message(message, name='Message')
        elif error_count > 0 or done_count > 0:
            total_product = done_count+error_count
            if error_count > 0:
                self.shop_status = "error"
            else:
                self.shop_status = "new"
            message = ("<b>{0} out of {1}</b> products are deleted".format(
                done_count, total_product))
            self.message_post(body=Markup(message))
            return self.env['wk.wizard.message'].genrated_message(message, name='Message')

    def button_show_debug_wizard(self):
        context = {'google_shop': self.id}
        return self.env['google.shop.debug'].with_context(context).genrated_wizard()
