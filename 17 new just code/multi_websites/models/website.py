# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2019-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################
import base64
import os
import re
from odoo import api, fields, models, tools, _
from odoo.tools import config
from odoo.exceptions import UserError
from lxml import etree
import logging
from odoo.http import request
_logger = logging.getLogger(__name__)


class Website(models.Model):
	_inherit = 'website'

	def has_google_analytics(self):
		self.has_google_analytics = bool(self.google_analytics_key)

	def has_google_analytics_dashboard(self):
		self.has_google_analytics_dashboard =  False #bool(self.google_management_client_id)

	def has_google_maps(self):
		self.has_google_maps = bool(self.google_maps_api_key)

	def inverse_has_google_analytics(self):
		if not self.has_google_analytics:
			self.has_google_analytics_dashboard = False
			self.google_analytics_key = False

	def inverse_has_google_maps(self):
		if not self.has_google_maps:
			self.google_maps_api_key = False

	# def inverse_has_google_analytics_dashboard(self):
	# 	if not self.has_google_analytics_dashboard:
	# 		self.google_management_client_id = False
	# 		self.google_management_client_secret = False


	website_categ_id = fields.Many2one(
		comodel_name = 'product.category',
		string = "Category",
	)
	carrier_ids = fields.Many2many(
		comodel_name = 'delivery.carrier',
		string = "Carriers",
	)
	acquirer_ids = fields.Many2many(
		comodel_name = 'payment.provider',
		string = "Acquirers",
	)
	website_menu_ids = fields.One2many(
		comodel_name='website.menu',
		inverse_name="website_id",
		string="Menu"
	)
	website_page_ids = fields.One2many(
		comodel_name='website.page',
		inverse_name="website_id",
		string="Pages"
	)
	product_pricelist_ids = fields.Many2many(
		comodel_name='product.pricelist',
		string="Pricelist"
	)
	website_category_ids = fields.One2many(
		'product.public.category',
		"website_id",
		string="Ecommerce Categories"
	)
	color = fields.Integer(string='Color Index')
	logo = fields.Binary(
		string="Logo")
	has_google_analytics = fields.Boolean(
		string="Google Analytics",
		compute=has_google_analytics,
		inverse=inverse_has_google_analytics)
	has_google_analytics_dashboard = fields.Boolean(
		string="Google Analytics Dashboard",
		compute=has_google_analytics_dashboard,)
		# inverse=inverse_has_google_analytics_dashboard)
	has_google_maps = fields.Boolean(
		string="Google Maps",
		compute=has_google_maps,
		inverse=inverse_has_google_maps)

	users_login_multi_websites = fields.Boolean(
		string="Allow all Users to login this website",
		help="All Users will be able to login in this website")

	product_tmpl_ids = fields.Many2many(comodel_name="product.template", string="Products")
	website_catgeories_ids = fields.Many2many(comodel_name="product.public.category", string="Website Catgories")

	def open_related_model_view(self):
		self.ensure_one()
		website_realted_record = self._context.get('website_realted_record')
		website_realted_model =  self._context.get('website_realted_model')
		record_ids = self.read([website_realted_record])[0].get(website_realted_record)
		return {
			'name': ('Data'),
			'type': 'ir.actions.act_window',
			'view_mode': 'tree,form',
			'res_model': website_realted_model,
			'view_id': False,
			'domain': [('id', 'in', record_ids)],
			'target': 'current',
		}

	def website_go_to(self):
		self._force()
		return {
			'type': 'ir.actions.act_url',
			'url': '/',
			'target': 'self',
		}

	def install_theme_on_current_website(self):
		self._force()
		action = self.env["ir.actions.actions"]._for_xml_id("website.theme_install_kanban_action")
		action['target'] = 'main'
		return action

	def _compute_pricelist_ids(self):
		res = super(Website, self)._compute_pricelist_ids()
		website = self.env['website'].get_current_website()
		if website.product_pricelist_ids:
			self.pricelist_ids = website.product_pricelist_ids.ids
		return res

	def sale_product_domain(self):
		cur_website = self.get_current_website()
		product_tmpl_ids = cur_website.product_tmpl_ids.ids
		return [("sale_ok", "=", True)] + self.get_current_website().website_domain() + ['|',('website_ids','=',False),('id','in',product_tmpl_ids)]

	# For demo purpose only 
	"""@api.model
	def set_domain(self):
		base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
		if len(base_url.split(':')) > 1:
			for website in self.env['website'].search([]):
				website.domain = website.domain + ':' + base_url.split(':')[-1]"""

	def write(self,vals):
		ctx = dict(self.env.context,wkWebsite=True)
		self.env.context = ctx
		return super(Website,self).write(vals)

class Page(models.Model):
	_inherit = 'website.page'
	
	def unlink(self):
		if self.env.context.get('wkWebsite',False):
			self.website_id= False
			self.is_published = False
			self.active = False
		else:
			return super(Page, self).unlink()

class WebsiteMenu(models.Model):
	_inherit = 'website.menu'

	def unlink(self):
		if self.env.context.get('wkWebsite',False):
			self.website_id= False
		else:
			return super(WebsiteMenu, self).unlink()

class ProductPublicCategory(models.Model):
	_inherit = "product.public.category"

	website_ids = fields.Many2many(comodel_name="website", string="Allowed Websites")

	def unlink(self):
		if self.env.context.get('wkWebsite',False):
			self.website_id= False
		else:
			return super(ProductPublicCategory, self).unlink()

class DeliveryCarriers(models.Model):
	_inherit = 'delivery.carrier'

	@api.model_create_multi
	def create(self, vals_list):
		res_ids = super().create(vals_list)
		for rec in res_ids:
			website = rec.website_id
			if website:
				website.sudo().write({'carrier_ids': [(4,rec.id)]})
			else:
				for website in self.env['website'].sudo().search([]):
					website.sudo().write({'carrier_ids': [(4,rec.id)]})
		return res_ids
	
	def write(self, vals):
		res_id = super().write(vals)
		if vals.get('website_id') != None:
			website_ids = self.env['website'].sudo().search([])
			for website in website_ids:
				website.sudo().write({'carrier_ids': [(3, self.id)]})
			if vals.get('website_id'):
				website = self.env['website'].sudo().browse([vals.get('website_id')])
				website.sudo().write({'carrier_ids': [(4, self.id)]})
			else:
				for website in website_ids:
					website.sudo().write({'carrier_ids': [(4, self.id)]})				
		return res_id
