# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
from odoo import fields, models
from ..hubspot_bridge import Bridge
import logging

_logger = logging.getLogger(__name__)


class ChannelConnection(models.Model):
	_inherit = 'channel.connection'

	def _set_info(self):
		if self.channel=='hubspot':
			self.blog_url = 'https://webkul.com/blog/?s=odoo'
		else:
			super()._set_info()

	hubspot_api_key = fields.Char(copy=False)
	channel = fields.Selection(
		selection_add=[('hubspot', 'Hubspot')],
		ondelete={'hubspot': 'cascade'},
		copy=False
	)

	product_properties = fields.One2many('hubspot.custom.field','connection_id','Product Custom Properties',domain=[('object_type','=','product')])
	conatct_properties = fields.One2many('hubspot.custom.field','connection_id','Contact Custom Properties',domain=[('object_type','=','partner')])
	company_properties = fields.One2many('hubspot.custom.field','connection_id','Company Custom Properties',domain=[('object_type','=','company')])
	lead_properties = fields.One2many('hubspot.custom.field','connection_id','Lead Custom Properties',domain=[('object_type','=','lead')])
	
	hs_auth_type = fields.Selection([('h_api_key', 'Hubspot API Key'),('h_access_token', 'Hubspot Access Token')],
							help='''There are two options are available select: 
						1- Hubspot API Key:  you can use api_key which is available in your account of Hubspot.
						2- Hubspot Access Token: if you are using private app the use then this option is applicable.
								''',
						default='h_api_key'
				)


	def hubspot_connect(self):
		with Bridge(api_key=self.hubspot_api_key,auth_type=self.hs_auth_type) as bridge:
			try:
				stages_imported = bridge.connect()
				stages_imported_dict = {s[0]:s[1] for s in stages_imported}
				stages_imported = set(stages_imported_dict.keys())
				stages_mapped = set(self.stage_ids.mapped('remote_id'))
				stages_to_create = stages_imported - stages_mapped
				stages_to_delete = stages_mapped - stages_imported
				if stages_to_create:
					default_stage_id = self.env['crm.stage'].search([],limit=1).id
					stages = [
						{
							'name': stages_imported_dict[stage],
							'connection_id': self.id,
							'local_id': default_stage_id,
							'remote_id': stage,
						} 
						for stage in stages_to_create
					]
					self.env['channel.stage.mapping'].create(stages)
				if stages_to_delete:
					self.stage_ids.filtered(lambda x: x.name in stages_to_delete).unlink()
				self.connected = True
			except Exception as e:
				return False, f"Connection failed {e}."
			else:
				return True, "Connection successful. Kindly map imported default pipeline stages."

	def hubspot_import_data(self, object_type, object_filter='all',**kw,):
		with Bridge(api_key=self.hubspot_api_key,auth_type=self.hs_auth_type) as bridge:
			custom_field_obj = self.env['hubspot.custom.field'].search([('object_type','=',object_type)])
			f = getattr(bridge, f'get_{object_type}', None)
			if not f:
				raise NotImplementedError(f'Import {object_type} is not implemented for {self.channel}')
			if object_filter == 'id':
				object_id = kw['object_id']
				remote_ids, data_list, kw = f(custom_field_obj,object_id)
			else:
				remote_ids, data_list, kw = f(custom_field_obj,**kw)
		return remote_ids, data_list, kw

	def hubspot_export_data(self, model, records):
		success_ids = []
		error_ids = []
		log_lines_data = []
		if model == 'res.partner':
			object_type = 'partner'
		elif model == 'crm.lead':
			object_type = 'deal'
			bridge_method = 'post_deal'
		elif model == 'product.template':
			object_type = 'product'
			bridge_method = 'post_product'
		else:
			raise NotImplementedError('Not Implemented')
		with Bridge(api_key=self.hubspot_api_key,auth_type=self.hs_auth_type) as bridge:
			for record in records:
				list_data = []
				log_line_data = {'local_id': record.id}
				try:
					data = self.hubspot_get_data(record)
					if(record.activity_ids):
						activity_data = self.get_activities_data(record)
						list_data.append([data,activity_data])
					
					else:
						list_data.append([data,False])
					if object_type == 'partner':
						if record.is_company:
							bridge_method = 'post_company'
						else:
							bridge_method = 'post_contact'

					f = getattr(bridge, bridge_method, None)
					if not f:
						raise NotImplementedError(f'Export {object_type} is not implemented for {self.channel}')
					for list_datas in list_data:
						res = f(list_datas)
				except NotImplementedError as e:
					raise e
				except Exception as e:
					log_line_data['error'] = str(e)
					error_ids.append(str(record.id))
				else:
					success_ids.append(str(record.id))
					log_line_data.update(
						success=True,
						remote_id=res.get("id"),
					)
					respone = self.env[f'{model}.mapping'].create(
						{
							'connection_id': self.id,
							'local_id': record.id,
							'remote_id': res.get("id"),
						}
					)

					# ------------------------- Activites Mappings---------------------

					if(list_datas[1] != False):
						for activity in record.activity_ids:
							activity_vals = {
										"odoo_id": record.activity_ids.id,
										"activity_type": activity.activity_type_id.id,
										"hubspot_id": res.get('activity_obj_id'),
										"activity_object_type": object_type,
									}
							if(record.is_company):
								activity_vals["activity_object_type"] = "company"
							if(model == 'res.partner'):
								activity_vals["crm_partner_id"] = respone.id
							elif(model == 'crm.lead'):
								activity_vals["crm_lead_id"] = respone.id
							self.env['hubspot.activity.mapping'].create(activity_vals)
					
				log_lines_data.append((0, 0, log_line_data))
		return success_ids, error_ids, log_lines_data

	def hubspot_update_data(self, model, mappings):
		list_data = []
		success_ids = []
		error_ids = []
		log_lines_data = []
		if model == 'res.partner':
			object_type = 'partner'
		elif model == 'crm.lead':
			object_type = 'deal'
			bridge_method = 'put_deal'
		elif model == 'product.template':
			object_type = 'product'
			bridge_method = 'put_product'
		else:
			raise NotImplementedError('Not Implemented')

		with Bridge(api_key=self.hubspot_api_key,auth_type=self.hs_auth_type) as bridge:
			for mapping in mappings:
				record = mapping.local_id
				log_line_data = {'local_id': record.id}
				try:
					data = self.hubspot_get_data(record)
					if(record.activity_ids):
						activity_data = self.get_activities_data(record)
						list_data.append([data,activity_data])
					else:
						list_data.append([data,False])

					if object_type == 'partner':
						if record.is_company:
							bridge_method = 'put_company'
						else:
							bridge_method = 'put_contact'

					f = getattr(bridge, bridge_method, None)
					if not f:
						raise NotImplementedError(f'Update {object_type} is not implemented for {self.channel}')
					
					if(list_data):
						for list_datas in list_data:
							res = f(mapping.remote_id,list_datas)
					# else:
					# 	res = f(mapping.remote_id,data)
					# res = f(mapping.remote_id,data)
					
				except NotImplementedError as e:
					raise e
				except Exception as e:
					log_line_data['error'] = str(e)
					error_ids.append(str(record.id))
				else:
					success_ids.append(str(record.id))
					log_line_data.update(
						success=True,
						remote_id=res.get("id"),
					)

					# ------------------------- Activites Mappings---------------------

					if(list_datas[1] != False):	
						for activity in record.activity_ids:
							activity_mapping = self.env['hubspot.activity.mapping'].search([('odoo_id','=',activity.id)])
							if(not activity_mapping):
								activity_vals = {
											"odoo_id": activity.id,
											"activity_type": activity.activity_type_id.id,
											"hubspot_id": res.get('activity_obj_id'),
											"activity_object_type": object_type,
										}
								if(model == 'res.partner'):
									activity_vals["crm_partner_id"] = mapping.id
									if(record.is_company):
										activity_vals["activity_object_type"] = "company"
								elif(model == 'crm.lead'):
									activity_vals["crm_lead_id"] = mapping.id
								self.env['hubspot.activity.mapping'].create(activity_vals)
				log_lines_data.append((0, 0, log_line_data))
		return success_ids, error_ids, log_lines_data

	def hubspot_get_data(self, record):
		if record._name == 'res.partner':
			if record.is_company:
				data = self.hubspot_get_company_data(record)
			else:
				data = self.hubspot_get_contact_data(record)

		elif record._name == 'crm.lead':
			data = self.hubspot_get_deal_data(record)
		elif record._name == 'product.template':
			data = self.hubspot_get_product_data(record)
		else:
			raise NotImplementedError('Not Implemented')
		return data

	def hubspot_get_company_data(self, record):

		hubspot_user = self.env["res.users.mapping"].search([('local_id','=',record.user_id.id)])
		if(not hubspot_user):
				hubspot_user = self.env["res.users.mapping"].search([('local_id','=',record.user_id.id)])
				if(not hubspot_user):
					hubspot_user = self.env["res.users.mapping"].search([('local_id','=',self.default_user_id.id)])
		data =  {
			'name': record.name or "",
			'city': record.city or "",
			'state': record.state_id.name or "",
			'phone': record.phone or "",
			'domain': record.website or "",
			# 'industry':','.join(record.category_id.mapped('name')),
			'hubspot_owner_id': hubspot_user.remote_id or ""
		}

		custom_map = self.env['hubspot.custom.field'].search([('connection_id','=',self.id),('object_type','=',"company")])
		if(custom_map):
			for custom_field in custom_map:
				if custom_field:
					res = getattr(record, custom_field.odoo_name,None)
					hubspot_field = custom_field.hubspot_name
					data[hubspot_field] = res
		return data


	def hubspot_get_contact_data(self, record):
		hubspot_user = self.env["res.users.mapping"].search([('local_id','=',record.user_id.id)])
		if(not hubspot_user):
				hubspot_user = self.env["res.users.mapping"].search([('local_id','=',record.user_id.id)])
				if(not hubspot_user):
					hubspot_user = self.env["res.users.mapping"].search([('local_id','=',self.default_user_id.id)])
		data={
			'phone': record.phone or "",
			'email': record.email or "",
			# 'company': record.parent_id.name,
			'website': record.website or "",
			'hubspot_owner_id': hubspot_user.remote_id or ""
		}
		custom_map = self.env['hubspot.custom.field'].search([('connection_id','=',self.id),('object_type','=',"partner")])
		if(custom_map):
			for custom_field in custom_map:
				if custom_field:
					res = getattr(record, custom_field.odoo_name,None)
					hubspot_field = custom_field.hubspot_name
					data[hubspot_field] = res

		name = record.name
		i = name.rfind(' ')
		if i:
			data['firstname'] = name[:i]
			data['lastname'] = name[i+1:]
		else:
			data['firstname'] = name[:i]
		if record.parent_id:
			parent_mapping = record.parent_id.mapping_ids.filtered(
				lambda x: x.connection_id == self
			)
			if parent_mapping:
				data['company_id'] = parent_mapping.remote_id
			else:
				raise ValueError(f'Company {record.parent_id} is not mapped.')
		return data

	def hubspot_get_deal_data(self, record):

		hubspot_user = self.env["res.users.mapping"].search([('local_id','=',record.user_id.id)])
		if(not hubspot_user):
				hubspot_user = self.env["res.users.mapping"].search([('local_id','=',record.user_id.id)])
				if(not hubspot_user):
					hubspot_user = self.env["res.users.mapping"].search([('local_id','=',self.default_user_id.id)])
		data = {
			'dealname': record.name or "",
			'amount': record.expected_revenue or "",
			'closedate': record.date_deadline or "",
			'hubspot_owner_id': hubspot_user.remote_id or "",
			'pipeline': 'default'
		}
		custom_map = self.env['hubspot.custom.field'].search([('connection_id','=',self.id),('object_type','=',"lead")])
		if(custom_map):
			for custom_field in custom_map:
				if custom_field:
					res = getattr(record, custom_field.odoo_name,None)
					hubspot_field = custom_field.hubspot_name
					data[hubspot_field] = res

		stage_mapping = self.env['channel.stage.mapping'].search(
			[
				('connection_id','=',self.id),
				('local_id','=',record.stage_id.id),
			],
			limit=1,
		)
		if stage_mapping:
			data['dealstage'] = stage_mapping.remote_id
		else:
			raise NotImplementedError('Not Implemented')
		parter_id = record.partner_id
		if parter_id:
			parent_mapping = parter_id.mapping_ids.filtered(
				lambda x: x.connection_id == self
			)
			if parent_mapping:
				if parent_mapping.is_company:
					data['company_id'] = parent_mapping.remote_id
				else:
					data['contact_id'] = parent_mapping.remote_id
			else:
				raise ValueError(f'Contact {record.parent_id} is not mapped.')
		return data

	def hubspot_get_product_data(self, record):
		
		data = {
			'name': record.name or "",
			'price': record.list_price or "",
			'description': record.description_sale or '',
			'hs_sku': record.default_code or '',
			'hs_cost_of_goods_sold': record.standard_price or '',
		}

		custom_map = self.env['hubspot.custom.field'].search([('connection_id','=',self.id),('object_type','=',"product")])
		if(custom_map):
			for custom_field in custom_map:
				if custom_field:
					res = getattr(record, custom_field.odoo_name,None)
					hubspot_field = custom_field.hubspot_name
					data[hubspot_field] = res
		
		return data
	def hubspot_delete_data(self, model, mapping_data):
		
		success_ids = []
		error_ids = []
		log_lines_data = []
		if model == 'res.partner':
			object_type = 'partner'
		elif model == 'crm.lead':
			object_type = 'deal'
			bridge_method = 'delete_deal'
		elif model == 'product.template':
			object_type = 'product'
			bridge_method = 'delete_product'
		else:
			raise NotImplementedError('Not Implemented')
		with Bridge(api_key=self.hubspot_api_key,auth_type=self.hs_auth_type) as bridge:
			for mapping in mapping_data:
				log_line_data = {'local_id': mapping.id}
				try:
					if object_type == 'partner':
						if mapping_data.local_id.is_company:
							bridge_method = 'delete_company'
						else:
							bridge_method = 'delete_contact'
					f = getattr(bridge, bridge_method, None)
					if not f:
						raise NotImplementedError(f'Export {object_type} is not implemented for {self.channel}')
					res = f(mapping_data.remote_id)
				except NotImplementedError as e:
					raise e
				except Exception as e:
					log_line_data['error'] = str(e)
					error_ids.append(str(mapping_data))
				else:
					success_ids.append(str(mapping_data.local_id.id))
					log_line_data.update(
						success=True,
						# remote_id=res.id,
					)
				log_lines_data.append((0, 0, log_line_data))
		return success_ids, error_ids, log_lines_data
	

	# ------------------------- Geting Odoo Activites data for creating activites on hubspot ---------------------

	def get_activities_data(self, record):
		activity_list = []
		for activity_id in record.activity_ids:
			hubspot_user = self.env["res.users.mapping"].search([('local_id','=',activity_id.user_id.id)])
			if(not hubspot_user):
				hubspot_user = self.env["res.users.mapping"].search([('local_id','=',record.user_id.id)])
				if(not hubspot_user):
					hubspot_user = self.env["res.users.mapping"].search([('local_id','=',self.default_user_id.id)])

			type = activity_id.activity_type_id.name
			activity_mapping = self.env['hubspot.activity.mapping'].search([('odoo_id','=',activity_id.id)])
			if(not activity_mapping):
				if(type == "Email"):
					data = {
						'hs_timestamp': activity_id.date_deadline or "",
						'hubspot_owner_id': hubspot_user.remote_id or "",
						'hs_email_direction': "EMAIL" or "",
						'hs_email_status': "SENT" or "",
						'hs_email_subject': activity_id.summary or "",
						'hs_email_text': str(activity_id.note) or "",
						'type' : type or "",
					}
					if(record._name == "res.partner"):
						data['associationTypeId'] = 10

					if(record._name == "crm.lead"):
						data['associationTypeId'] = 12

					if(record._name == "res.partner" and record.is_company):
						data['associationTypeId'] = 8

				elif(type == "Meeting"):
					data = {
							"hs_timestamp": activity_id.date_deadline or "",
							"hubspot_owner_id": hubspot_user.remote_id or "",
							"hs_meeting_body": activity_id.summary or "",
							'type' : type or "",
							# "hs_meeting_title": "Intro meeting",
							# "hs_internal_meeting_notes": "These are the meeting notes",
							# "hs_meeting_external_url": "https://Zoom.com/0000",
							# "hs_meeting_location": "Remote",
							# "hs_meeting_start_time": "2021-03-23T01:02:44.872Z",
							# "hs_meeting_end_time": "2021-03-23T01:52:44.872Z",
							# "hs_meeting_outcome": "SCHEDULED"
							}
					if(record._name == "res.partner"):
						data['associationTypeId'] = 10

					if(record._name == "crm.lead"):
						data['associationTypeId'] = 12

					if(record._name == "res.partner" and record.is_company):
						data['associationTypeId'] = 8

				elif(type == "Call"):
					data = {
								"hs_timestamp": activity_id.date_deadline or "",
								"hs_call_title": activity_id.summary or "",
								"hubspot_owner_id": hubspot_user.remote_id or "",
								"hs_call_body": activity_id.note or "",
								'type' : type or "",
								# "hs_call_duration": "3800",
								# "hs_call_from_number": "(857)Ï829 5489",
								# "hs_call_to_number": "(509) 999 9999",
								# "hs_call_recording_url": "https://api.twilio.com/2010-04-01/Accounts/AC890b8e6fbe0d989bb9158e26046a8dde/Recordings/RE3079ac919116b2d22",
								# "hs_call_status": "COMPLETED"
							}
					if(record._name == "res.partner"):
						data['associationTypeId'] = 10

					if(record._name == "crm.lead"):
						data['associationTypeId'] = 12

					if(record._name == "res.partner" and record.is_company):
						data['associationTypeId'] = 8
					
				elif(type == "To-Do"):
					data = {
								"hs_timestamp": activity_id.date_deadline or "",
								"hs_note_body": str(activity_id.note) or "",
								"hubspot_owner_id":  hubspot_user.remote_id or "",
								'type' : type,
							}
					if(record._name == "res.partner"):
						data['associationTypeId'] = 10

					if(record._name == "crm.lead"):
						data['associationTypeId'] = 12

					if(record._name == "res.partner" and record.is_company):
						data['associationTypeId'] = 8

				activity_list.append(data)
		return activity_list
	
	def update_activities(self, obj_id, activity_type):

		with Bridge(api_key=self.hubspot_api_key,auth_type=self.hs_auth_type) as bridge:
			res = bridge.put_activities(obj_id, activity_type)

		return res
