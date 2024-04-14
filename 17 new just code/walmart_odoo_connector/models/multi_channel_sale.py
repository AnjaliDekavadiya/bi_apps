# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2020-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

from logging import getLogger

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from ..walmart_api import WalmartConnect


_logger = getLogger(__name__)

MARKETPLACES = [
    ("US", "United States"),
    ("CA", "Canada"),
    ("MX", "Mexico"),
]
OrderCancellationReason = [
    ("1", "Customer Request(Cancel)"),
    ("2", "Out of Stock"),
    ("3", "Duplicate Order"),
    ("4", "Change Order"),
    ("5", "Incorrect Address"),
    ("6", "Fraud Detected"),
    ("7", "Price Error"),
]


class MultiChannelSale(models.Model):
    _inherit = 'multi.channel.sale'

    walmart_client_id = fields.Char("Client Id")
    walmart_client_secret = fields.Char("Client Secret")
    walmart_channel_type = fields.Char("Channel Type")
    walmart_access_token = fields.Char("Access Token")
    walmart_marketplace = fields.Selection(
        MARKETPLACES, "Marketplace", default="US")
    walmart_default_tax_code = fields.Char("Tax Code", default='2038711')
    walmart_default_cancel_reason = fields.Selection(
        OrderCancellationReason, "Cancel Reason")

    # Cron Setting
    walmart_update_mapping = fields.Boolean()

    # Order Real-time Order Active/Inactive Hook
    walmart_auto_sync_order = fields.Boolean("Auto Order Sync",
        help = """
            Enable/Disable realtime order sync.
            a) Enabling it will check test realtime sync necessary condition
                and will activate it.
            b) Disabling will inactivate the realtime sync.
        """
    )
    walmart_auto_sync_order_status = fields.Html(readonly=True)

    @api.constrains('walmart_default_tax_code')
    def _check_walmart_default_tax_code(self):
        if self.walmart_default_tax_code:
            try:
                int(self.walmart_default_tax_code)
            except:
                raise ValidationError('Alphabetic Tax Code Error')

    @api.constrains('walmart_auto_sync_order')
    def toggle_walmart_auto_sync_order(self):
        if self.channel == 'walmart' and self.walmart_marketplace == 'US':
            if self.environment == "production":
                production = True
                sandbox = False
            else:
                production = False
                sandbox = True
            with WalmartConnect(self.walmart_client_id, self.walmart_client_secret, self, self.walmart_access_token,
                self.walmart_channel_type, self.walmart_marketplace, sandbox, production) as Connect:
                Connect.checkTokenExpiry()
                if self.walmart_auto_sync_order:
                    if Connect.testRealtimeOrderSync():
                        Connect.registerRealtimeOrderHook()
                        status = "<p class='text-success'>Realtime Order Sync tested and enabled</p>"
                    else:
                        status = "<p class='text-danger'>Realtime order sync testing failed</p>"
                else:
                    Connect.deregisterRealtimeOrderHook()
                    status = "<p class='text-info'>Realtime Order Sync now disabled</p>"

                self.walmart_auto_sync_order_status = status

    def write(self, vals):
        for rec in self:
            if 'environment' in vals and rec.state=='validate' and rec.channel == 'walmart':
                vals['state'] = 'draft'
        return super(MultiChannelSale, self).write(vals)

    @api.model
    def get_channel(self):
        channels = super(MultiChannelSale, self).get_channel()
        channels.append(('walmart', 'Walmart'))
        return channels

    def get_core_feature_compatible_channels(self):
        vals = super(MultiChannelSale,
                     self).get_core_feature_compatible_channels()
        vals.append('walmart')
        return vals

    def connect_walmart(self):
        if self.environment == "production":
            production = True
            sandbox = False
        else:
            production = False
            sandbox = True
        martketplace = self.walmart_marketplace
        with WalmartConnect(self.walmart_client_id, self.walmart_client_secret, self, self.walmart_access_token,
            self.walmart_channel_type, martketplace, sandbox, production) as Connect:

            if martketplace!="CA":
                response = Connect.checkTokenExpiry() #If token is expired it will update it too
            else:
                response = Connect._call_feeds_api()
            success = True
            msg = """
				<p style='color:green'>
					Successfully connected to Walmart
				</p>
			"""
            if response.get("error"):
                msg = response.get("error")
                success = False
                msg = """
					# 		<p>Failed to connect to Walmart due to</p>
					# 		<p style='color:red'>{}</p>
					# 	""".format(msg)
            return success, msg

    def action_walmart_feed_wizard(self):
        record = self.env["walmart.feed"].create(
            {
                "channel_id": self.id,
            }
        )
        return {
            'name': "Walmart Feed Status Check Wizard",
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'walmart.feed',
            'res_id': record.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
        }

    ##################
    # Import Process #
    ##################

    def import_walmart(self, object, **kw):
        if self.environment == "production":
            production = True
            sandbox = False
        else:
            production = False
            sandbox = True
        martketplace = self.walmart_marketplace
        with WalmartConnect(self.walmart_client_id, self.walmart_client_secret, self, self.walmart_access_token,
            self.walmart_channel_type, martketplace, sandbox, production) as Connect:
            if martketplace != "CA":
                Connect.checkTokenExpiry() #If token is expired it will update it too
            if object == "product.category":
                return Connect.getCategories(**kw)
            elif object == "product.template":
                return Connect.getTemplates(**kw)
            elif object == "sale.order":
                return Connect.getOrders(**kw)
            elif object == 'delivery.carrier':
                return Connect.getShippingMethods(**kw)
            else:
                raise Exception("<span class='text-danger'>Not Applicable for Walmart instance</span>")

    ##################
    # Export Process #
    ##################

    def export_walmart(self, record, **kw):
        obj = object
        res = False
        if self.environment == "production":
            production = True
            sandbox = False
        else:
            production = False
            sandbox = True
        martketplace = self.walmart_marketplace
        if record.wk_walmart_ok and record.sale_ok:
            with WalmartConnect(self.walmart_client_id, self.walmart_client_secret, self, self.walmart_access_token,
            self.walmart_channel_type, martketplace, sandbox, production) as Connect:
                if martketplace != "CA":
                    Connect.checkTokenExpiry() #If token is expired it will update it too
                res, obj = Connect.postTemplate(record)
        return res, obj

    ##################
    # Update Process #
    ##################

    def update_walmart(self, record, **kw):
        if self.environment == "production":
            production = True
            sandbox = False
        else:
            production = False
            sandbox = True
        martketplace = self.walmart_marketplace
        with WalmartConnect(self.walmart_client_id, self.walmart_client_secret, self, self.walmart_access_token,
            self.walmart_channel_type, martketplace, sandbox, production) as Connect:
                if martketplace != "CA":
                    Connect.checkTokenExpiry() #If token is expired it will update it too
                res, object = Connect.updateTemplate(record)
                return res, object

    ################
    # Base Methods #
    ################

    def walmart_post_do_transfer(self, stock_picking, mapping_ids, result):
        shipped = False
        if self.environment == "production":
            production = True
            sandbox = False
        else:
            production = False
            sandbox = True
        martketplace = self.walmart_marketplace

        order_status = self.order_state_ids.filtered('odoo_ship_order')[0]
        status = order_status.channel_state
        wm_order_id = mapping_ids.store_order_id

        with WalmartConnect(self.walmart_client_id, self.walmart_client_secret, self, self.walmart_access_token,
            self.walmart_channel_type, martketplace, sandbox, production) as Connect:
            if martketplace != "CA":
                Connect.checkTokenExpiry() #If token is expired it will update it too
            shipped = Connect.markOrderAsShipped(wm_order_id)

    def walmart_post_cancel_order(self, sale_order, mapping_ids, result):
        status = False
        order_status = self.order_state_ids.filtered(
            lambda order_state_id: order_state_id.odoo_order_state == 'cancelled')
        if order_status:
            if self.environment == "production":
                production = True
                sandbox = False
            else:
                production = False
                sandbox = True
            martketplace = self.walmart_marketplace

            order_status = self.order_state_ids.filtered('odoo_ship_order')[0]
            status = order_status.channel_state
            wm_order_id = mapping_ids.store_order_id

            with WalmartConnect(self.walmart_client_id, self.walmart_client_secret, self,
                self.walmart_access_token, self.walmart_channel_type, martketplace,
                sandbox, production) as Connect:
                status = Connect.cancelCompleteOrder(wm_order_id)
        return status

    def walmart_post_reverse_move(self, move_ids, mapping_ids):
        '''Order must be shipped for its refund to generated'''
        status = False
        order_status = self.order_state_ids.filtered(
            lambda order_state_id: order_state_id.odoo_order_state == 'refund')
        if order_status:
            if self.environment == "production":
                production = True
                sandbox = False
            else:
                production = False
                sandbox = True
            martketplace = self.walmart_marketplace
            wm_order_id = mapping_ids.store_order_id

            with WalmartConnect(self.walmart_client_id, self.walmart_client_secret, self,
                self.walmart_access_token, self.walmart_channel_type, martketplace,
                sandbox, production) as Connect:
                status = Connect.refundOrderLines(wm_order_id)
        return status

    def sync_quantity_walmart(self, mapping, qty):

        if self.environment == "production":
            production = True
            sandbox = False
        else:
            production = False
            sandbox = True
        martketplace = self.walmart_marketplace

        with WalmartConnect(self.walmart_client_id, self.walmart_client_secret, self, self.walmart_access_token,
            self.walmart_channel_type, martketplace, sandbox, production) as Connect:
            if martketplace != "CA":
                Connect.checkTokenExpiry() #If token is expired it will update it too
            return Connect.syncQuantity(mapping, qty)

    @api.model
    def match_template_mappings(self, store_product_id=None, domain=None, limit=1, **kwargs):
        channel = self.channel
        if channel != 'walmart':
            return super().match_template_mappings(
                store_product_id=store_product_id,
                domain=domain,
                limit=limit, **kwargs)
        map_domain = self.get_channel_domain(domain)
        map_domain += ['|', ('active', '=', False), ('active', '=', True)]

        if store_product_id and channel == 'walmart':
            map_domain += ['|', ('store_product_id',
                                 '=', store_product_id), ('store_product_id',
                                                          '=', store_product_id)]
        else:
            map_domain += [('store_product_id',
                            '=', store_product_id)]
        if kwargs.get('default_code'):
            map_domain += [('default_code', '=',
                            kwargs.get('default_code'))]
        if kwargs.get('barcode'):
            map_domain += [('barcode', '=', kwargs.get('barcode'))]
        mapping = self.env['channel.template.mappings'].search(
            map_domain, limit=limit)
        if channel == 'walmart' and mapping:
            mapping.active = True
            mapping.store_product_id = store_product_id
        return mapping

    @api.model
    def match_product_mappings(self, store_product_id=None, line_variant_ids=None,
                               domain=None, limit=1, **kwargs):
        channel = self.channel
        if channel != 'walmart':
            return super().match_product_mappings(
                store_product_id=store_product_id,
                line_variant_ids=line_variant_ids,
                domain=domain,
                limit=limit, **kwargs)

        map_domain = self.get_channel_domain(domain)
        map_domain += ['|', ('active', '=', True), ('active', '=', False)]
        if store_product_id:
            map_domain += ['|', ('store_product_id',
                                 '!=', store_product_id), ('store_product_id', '=', store_product_id), ]
        if line_variant_ids:
            map_domain += [('store_variant_id', '=', line_variant_ids)]
        if kwargs.get('default_code'):
            map_domain += [('default_code', '=', kwargs.get('default_code'))]
        if kwargs.get('barcode'):
            map_domain += [('barcode', '=', kwargs.get('barcode'))]
        res = self.env['channel.product.mappings'].search(
            map_domain, limit=limit)
        return res

    @api.model
    def match_odoo_product(self, vals, obj='product.product'):
        oe_env = self.env[obj]
        record = False
        # check avoid_duplicity using default_code
        barcode = vals.get('barcode')
        if barcode:
            if self.channel == "walmart":
                record = oe_env.search(
                    [('barcode', 'in', [barcode, barcode.strip('0')])], limit=1)
            else:
                record = oe_env.search([('barcode', '=', barcode)], limit=1)
        if not record:
            default_code = vals.get('default_code')
            ir_values = self.default_multi_channel_values()
            if ir_values.get('avoid_duplicity') and default_code:
                record = oe_env.search(
                    [('default_code', '=', default_code)], limit=1)
            if not record:
                if 'product_template_attribute_value_ids' in vals and 'product_tmpl_id' in vals:
                    _ids = vals['product_template_attribute_value_ids'][0][2]
                    ids = ','.join([str(i) for i in sorted(_ids)])
                    domain = [('product_tmpl_id','=',vals['product_tmpl_id'])]
                    if ids:
                        domain += [('product_template_attribute_value_ids','in', _ids)]
                    record = oe_env.search(domain) \
                    .filtered(lambda prod: prod.product_template_attribute_value_ids._ids2str()==ids)
        return record

    ################
    # Import Crons #
    ################

    def walmart_import_order_cron(self):
        _logger.info('+++++++++++Import Walmart Order Cron Started++++++++++++')
        kw = dict(
            object = 'sale.order',
            walmart_filter_type='by_date',
            walmart_import_date_from=self.import_order_date,
            from_cron = True,
        )
        self.env['import.operation'].create({
            'channel_id':self.id ,
        }).import_with_filter(**kw)

    #################
    # Mapping Crons #
    #################

    def cron_update_template_mapping(self):
        walmart_instance_ids = self.search([
                        ('state','=','validate'),
                        ('walmart_update_mapping','=',True)])
        for instance_id in walmart_instance_ids:
            if instance_id.environment == "production":
                production = True
                sandbox = False
            else:
                production = False
                sandbox = True
            martketplace = instance_id.walmart_marketplace

            with WalmartConnect(instance_id.walmart_client_id, instance_id.walmart_client_secret,
                        instance_id, instance_id.walmart_access_token, instance_id.walmart_channel_type, martketplace, sandbox, production) as Connect:
                if martketplace!="CA":
                    Connect.checkTokenExpiry() #If token is expired it will update it too
                return Connect.updateTemplateMapping()
