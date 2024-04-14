# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2020-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
from odoo.addons.odoo_multi_channel_sale import ApiTransaction

METAMAP = {
    'product.template': {
		'model'       : 'channel.template.mappings',
		'local_field' : 'odoo_template_id',
		'remote_field': 'store_product_id'
	},
	'product.product': {
		'model'       : 'channel.product.mappings',
		'local_field' : 'erp_product_id',
		'remote_field': 'store_variant_id'
	}
}

from odoo import models, exceptions
import logging
_logger = logging.getLogger(__name__)


class WalmartTransaction(ApiTransaction.Transaction):

    def create_mapping(self, local_record, remote_object):
        if self.channel == "walmart":
            if local_record._name == 'product.template':
                self.env['channel.template.mappings'].create(
                    {
                        'active': False,
                        'channel_id': self.instance.id,
                        'ecom_store': self.instance.channel,
                        'template_name': local_record.id,
                        'odoo_template_id': local_record.id,
                        'default_code': local_record.default_code,
                        'barcode': local_record.barcode,
                        'store_product_id': remote_object['id'],
                        'operation': 'export',
                    }
                )
                for local_variant, remote_variant in zip(local_record.product_variant_ids, remote_object['variants']):
                    self.env['channel.product.mappings'].create(
                        {
                            'active': False,
                            'channel_id': self.instance.id,
                            'ecom_store': self.instance.channel,
                            'product_name': local_variant.id,
                            'erp_product_id': local_variant.id,
                            'default_code': local_variant.default_code,
                            'barcode': local_variant.barcode,
                            'store_product_id': remote_object['id'],
                            'store_variant_id': remote_variant['id']
                        }
                    )
            elif local_record._name == 'product.product':
                template = local_record.product_tmpl_id
                domain = [('template_name', '=', template.id),
                          ('channel_id', '=', self.instance.id)]
                tmpl_mapping = self.env['channel.template.mappings'].search(
                    domain, limit=1)
                if not tmpl_mapping:
                    domain += [
                        ('active', '=', False)
                    ]
                    tmpl_mapping = self.env['channel.template.mappings'].search(
                        domain, limit=1)
                if tmpl_mapping:
                    self.env['channel.product.mappings'].create(
                        {
                            'active': False,
                            'channel_id': self.instance.id,
                            'ecom_store': self.instance.channel,
                            'product_name': local_record.id,
                            'erp_product_id': local_record.id,
                            'default_code': local_record.default_code,
                            'barcode': local_record.barcode,
                            'store_product_id': tmpl_mapping.store_product_id or remote_object['id'],
                            'store_variant_id': remote_object['id']
                        }
                    )
                else:
                    self.env['channel.template.mappings'].create(
                        {
                            'active': False,
                            'channel_id': self.instance.id,
                            'ecom_store': self.instance.channel,
                            'template_name': template.id,
                            'odoo_template_id': template.id,
                            'default_code': template.default_code,
                            'barcode': template.barcode,
                            'store_product_id': remote_object['id'],
                            'operation': 'export',
                        }
                    )
                    res = zip(local_record.product_variant_ids.filtered_domain([('id', '=', local_record.id)]),
                              remote_object['variants'])
                    for local_variant, remote_variant in res:
                        res = self.env['channel.product.mappings'].create(
                            {
                                'active': False,
                                'channel_id': self.instance.id,
                                'ecom_store': self.instance.channel,
                                'product_name': local_variant.id,
                                'erp_product_id': local_variant.id,
                                'default_code': local_variant.default_code,
                                'barcode': local_variant.barcode,
                                'store_product_id': remote_object['id'],
                                'store_variant_id': remote_variant['id']
                            }
                        )

        else:
            return super(WalmartTransaction, self).create_mapping(local_record, remote_object)

    def walmart_export_data(self, object, object_ids, operation='export'):
        msg = "Selected Channel doesn't allow it."
        if object == 'product.category':
            return self.display_message("<p class='text-info'>Not Applicable for Walmart instance</p>")
        success_ids, error_ids = [], []
        mappings = self.env[METAMAP.get(object).get('model')].search(
            [
                '|', ('active', '=', True),
                ('active', '=', False),
                ('channel_id', '=', self.instance.id),
                (
                    METAMAP.get(object).get('local_field'),
                    'in',
                    object_ids
                )
            ]
        )
        local_ids = mappings.mapped(
            lambda mapping: int(
                getattr(mapping, METAMAP.get(object).get('local_field')))
        )
        if operation == 'export' and hasattr(self.instance, 'export_{}'.format(self.channel)):
            msg = ''
            local_ids = set(object_ids)-set(local_ids)
            if not local_ids:
                return self.display_message(
                    """<p style='color:orange'>
			Selected records have already been exported.
		</p>"""
                )
            operation = 'exported'
            remote_object = ""
            for record in self.env[object].browse(local_ids):
                res, remote_object = getattr(
                    self.instance, 'export_{}'.format(self.channel))(record)
                if res:
                    self.create_mapping(record, remote_object)
                    success_ids.append(record.id)
                else:
                    msg = ''
                    error_ids.append(record.id)
            if success_ids and self.channel == "walmart":
                msg += f'''Exported, need to check status later
				<pre> FeedIDS: {remote_object['id']}</pre>\n'''
        elif operation == 'update' and hasattr(self.instance, 'update_{}'.format(self.channel)):
            msg = ''

            if not local_ids:
                return self.display_message(
                    """ <p style='color:orange'>
							Selected records haven't been exported yet.
						</p>"""
                )
            operation = 'updated'
            remote_object = ""
            for record in self.env[object].browse(local_ids):
                try:
                    res, remote_object = getattr(self.instance, 'update_{}'.format(self.channel))(
                        record=record,
                        get_remote_id=self.get_remote_id
                    )
                    if res:
                        success_ids.append(record.id)
                    else:
                        error_ids.append(record.id)
                except NotImplementedError:
                    raise exceptions.Warning("Not Possible")

            if self.channel == "walmart" and success_ids:
                msg += f'''Updated, need to check status later
			<pre> FeedID: {remote_object}</pre>'''
        if not msg:
            if success_ids:
                msg += f"<p style='color:green'>{success_ids} {operation}.</p>"
            if error_ids:
                msg += f"<p style='color:red'>{error_ids} not {operation}.</p>"
        return self.display_message(msg)


class ExportOperation(models.TransientModel):
    _inherit = 'export.operation'

    def export_button(self):
        if self.channel=='walmart':
            if self._context.get('active_model','multi.channel.sale') == 'multi.channel.sale':
                return WalmartTransaction(channel=self.channel_id).walmart_export_data(
                        object=self.object,
                        object_ids=self.env[self.object].search([]).ids,
                        operation='export',
                    )
            else:
                return WalmartTransaction(channel=self.channel_id).walmart_export_data(
                        object=self._context.get('active_model'),
                        object_ids=self._context.get('active_ids'),
                        operation=self.operation,
                    )
        else:
            return super(ExportOperation, self).export_button()
