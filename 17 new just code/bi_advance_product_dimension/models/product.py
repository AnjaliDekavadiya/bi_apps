# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
#################################################################################

from odoo import api, fields, models
from datetime import datetime, timedelta
from odoo import api, fields, models, tools, _
import odoo.addons.decimal_precision as dp
import psycopg2
import itertools
from functools import reduce
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT


class ProductTemplate(models.Model):
	_inherit = 'product.template'

	dimension = fields.Boolean('Uses Dimensional Values')
	active_1 = fields.Boolean('Length')
	len_min_1 = fields.Float('Length Minimum')
	len_max_1 = fields.Float('Length Maximum')
	custom_uom_id = fields.Many2one('uom.uom', string="UOM Prompt")
	active_2 = fields.Boolean('Width')
	width_min_2 = fields.Float('Width Minimum')
	width_max_2 = fields.Float('Width Maximum')
	label = fields.Char('Label')
	active_3 = fields.Boolean('Height')
	height_min_3 = fields.Float('Height Minimum')
	height_max_3 = fields.Float('Height Maximum')


	@api.onchange('dimension')
	def onchange_dimension(self):
		if self.dimension:
			uom_srch = self.env['uom.uom'].search([('name', '=', 'ft')])
			if uom_srch:
				self.custom_uom_id = uom_srch.id
		return

	def create_variant_ids(self):
		Product = self.env["product.product"]
		for tmpl_id in self.with_context(active_test=False):
			# adding an attribute with only one value should not recreate product
			# write this attribute on every product to make sure we don't lose them
			variant_alone = tmpl_id.attribute_line_ids.filtered(lambda line: len(line.value_ids) == 1).mapped('value_ids')
			for value_id in variant_alone:
				updated_products = tmpl_id.product_variant_ids.filtered(lambda product: value_id.attribute_id not in product.mapped('attribute_value_ids.attribute_id'))
				updated_products.write({'attribute_value_ids': [(4, value_id.id)],
									'dimension':tmpl_id.dimension,
					'active_1' : tmpl_id.active_1,
					'len_min_1' :  tmpl_id.len_min_1,
					'len_max_1' :  tmpl_id.len_max_1,
					'custom_uom_id' :tmpl_id.custom_uom_id.id,
					'active_2' : tmpl_id.active_2,
					'width_min_2':tmpl_id.width_min_2,
					'width_max_2' :  tmpl_id.width_max_2,
					'label' : tmpl_id.label,
					'active_3' :  tmpl_id.active_3,
					'height_min_3' : tmpl_id.height_min_3,
					'height_max_3' : tmpl_id.height_max_3,
									})
			# list of values combination
			existing_variants = [set(variant.attribute_value_ids.ids) for variant in tmpl_id.product_variant_ids]
			variant_matrix = itertools.product(*(line.value_ids for line in tmpl_id.attribute_line_ids if line.value_ids and line.value_ids[0].attribute_id.create_variant))
			variant_matrix = map(lambda record_list: reduce(lambda x, y: x + y, record_list, self.env['product.attribute.value']), variant_matrix)
			to_create_variants = filter(lambda rec_set: set(rec_set.ids) not in existing_variants, variant_matrix)

			# check product
			variants_to_activate = self.env['product.product']
			variants_to_unlink = self.env['product.product']
			for product_id in tmpl_id.product_variant_ids:
				if not product_id.active and product_id.attribute_value_ids in variant_matrix:
					variants_to_activate |= product_id
				elif product_id.attribute_value_ids not in variant_matrix:
					variants_to_unlink |= product_id
			if variants_to_activate:
				variants_to_activate.write({'active': True})

			# create new product
			for variant_ids in to_create_variants:
				new_variant = Product.create({
					'product_tmpl_id': tmpl_id.id,
					'attribute_value_ids': [(6, 0, variant_ids.ids)],
					'dimension':tmpl_id.dimension,
					'active_1' : tmpl_id.active_1,
					'len_min_1' :  tmpl_id.len_min_1,
					'len_max_1' :  tmpl_id.len_max_1,
					'custom_uom_id' :tmpl_id.custom_uom_id.id,
					'active_2' : tmpl_id.active_2,
					'width_min_2':tmpl_id.width_min_2,
					'width_max_2' :  tmpl_id.width_max_2,
					'label' : tmpl_id.label,
					'active_3' :  tmpl_id.active_3,
					'height_min_3' : tmpl_id.height_min_3,
					'height_max_3' : tmpl_id.height_max_3,
									
					
				})

			# unlink or inactive product
			for variant in variants_to_unlink:
				try:
					with self._cr.savepoint(), tools.mute_logger('odoo.sql_db'):
						variant.unlink()
				# We catch all kind of exception to be sure that the operation doesn't fail.
				except (psycopg2.Error, except_orm):
					variant.write({'active': False})
					pass
		return True

class ProductProduct(models.Model):
	_inherit = 'product.product'


	dimension = fields.Boolean('Uses Dimensional Values')
	active_1 = fields.Boolean('Length')
	len_min_1 = fields.Float('Length Minimum')
	len_max_1 = fields.Float('Length Maximum')
	custom_uom_id = fields.Many2one('uom.uom', string="UOM Prompt")
	active_2 = fields.Boolean('Width')
	width_min_2 = fields.Float('Width Minimum')
	width_max_2 = fields.Float('Width Maximum')
	label = fields.Char('Label')
	active_3 = fields.Boolean('Height')
	height_min_3 = fields.Float('Height Minimum')
	height_max_3 = fields.Float('Height Maximum')


	@api.onchange('dimension')
	def onchange_dimension(self):
		if self.dimension:
			uom_srch = self.env['uom.uom'].search([('name', '=', 'ft')])
			if uom_srch:
				self.custom_uom_id = uom_srch.id
		return
			
