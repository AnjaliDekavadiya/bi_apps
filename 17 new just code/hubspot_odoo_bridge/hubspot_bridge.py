import json
import requests
from hubspot import HubSpot
from hubspot.crm.contacts.exceptions import ApiException as ContactApiException
from hubspot.crm.companies.exceptions import ApiException as CompanyApiException
from hubspot.crm.deals.exceptions import ApiException as DealApiException
from hubspot.crm.pipelines.exceptions import ApiException as PipelinesApiException
from hubspot.crm.products.exceptions import ApiException as ProductApiException
from hubspot.crm.owners.exceptions import ApiException as UserApiException
from hubspot.crm.objects.emails import SimplePublicObjectInputForCreate, ApiException
import logging

_logger = logging.getLogger(__name__)


COMPANY_PROPERTIES = ['name','industry','phone','domain','address','address2','city','zip',]
CONTACT_PROPERTIES = ['firstname','lastname','email','phone','city','jobtitle','website',]
DEAL_PROPERTIES = ['hubspot_owner_id','amount','closedate','dealname','dealstage','hs_priority']
PRODUCT_PROPERTIES = ['name','description','hs_cost_of_goods_sold','hs_sku','price']
PRIORITIES = {'low':'1','medium':'2','high':'3'}

# Hubspot activity data

EMAIL_ACTIVIY = ['hs_timestamp','hubspot_owner_id','hs_email_subject','hs_email_text']
MEETING_ACTIVIY = ['hs_timestamp','hubspot_owner_id','hs_meeting_body']
CALL_ACTIVIY = ['hs_timestamp','hs_call_title','hubspot_owner_id','hs_call_body']
NOTE_ACTIVIY = ['hs_timestamp','hs_note_body','hubspot_owner_id']


class Bridge:
	def __init__(self, api_key='',auth_type=''):
		self.auth_type = auth_type
		self.api_key = api_key
	def __enter__(self):
		if self.auth_type=='h_api_key':
			self.api = HubSpot(api_key=self.api_key)
		else:
			self.api = HubSpot(access_token=self.api_key)

		return self

	def __exit__(self,exc_type,exc_value,exc_traceback):
		del self

	def connect(self):
		return self.get_pipline_stage()

	def get_pipline_stage(self):
		try:
			res = self.api.crm.pipelines.pipeline_stages_api.get_all('deals', 'default')
		except PipelinesApiException as e:
			raise ValueError(e.reason)
		return {(stage.id,stage.label) for stage in res.results}

	def get_company(self,custom_field_obj, id=None, **kw):
		remote_ids = []
		data_list = []
		custom_filed = custom_field_obj.mapped('hubspot_name')
		try:
			if id:
				company = self.api.crm.companies.basic_api.get_by_id(id, properties=COMPANY_PROPERTIES + custom_filed)
				companies = [company]
				activities = self.get_activities(associations_type = ["company"])
				kw['done'] = True
			else:
				res = self.api.crm.companies.basic_api.get_page(
					properties=COMPANY_PROPERTIES + custom_filed,
					limit=kw['api_limit'],
					after=kw.get('next_page',0)
				)
				activities = self.get_activities(associations_type = ["contacts"])
				companies = res.results
				paging = res.paging
				if paging:
					kw['next_page'] = paging.next.after
				else:
					kw.update(
						next_page=str(int(kw.get('next_page',0))+1),
						done=True,
					)
		except CompanyApiException as e:
			raise ValueError(e.reason)
		for company in companies:
			properties = company.properties
			remote_ids.append(company.id)
			data = {
				'name': properties['name'],
				'category': properties.get('industry',False),
				'phone': properties.get('phone',False),
				'website': properties.get('domain',False),
				'street': properties.get('address',False),
				'street2': properties.get('address2',False),
				'city': properties.get('city',False),
				'zip': properties.get('zip',False),
			}

			for keys_exist in custom_field_obj:
				if(keys_exist.hubspot_name in properties):
					value = properties.get(keys_exist.hubspot_name)
					data[keys_exist.odoo_name] = value

			data_list.append(
				{
					'remote_id': company.id,
					'type': 'company',
					'data': json.dumps(data, indent=4, sort_keys=True),
				}
			)
			if(activities):
				active_list = []
				for activity in activities:
					dict = activity.to_dict()
					dict_data = dict.get("results")
					for data_dict in dict_data:
						if(data_dict.get("associations") != None):
							activity_type = data_dict.get("associations",False).get("contacts",False).get("results",False)[0].get("type",False)
							if data_dict.get("associations",False).get("contacts",False).get("results",False)[0].get("id",False) == company.id:
								data_activity = data_dict.get("properties",False)
								if(activity_type == 'call_to_contact'):
									activity_data = {
										"data_deadline":data_activity["hs_timestamp"],
										"summary":data_activity["hs_call_title"],
										"note":data_activity["hs_call_body"],
										"user_id":data_activity["hubspot_owner_id"],
										"object_id":data_activity["hs_object_id"],
										"activity_type":activity_type
									}
								elif(activity_type == 'email_to_contact'):
									activity_data = {
										"data_deadline":data_activity["hs_timestamp"],
										"summary":data_activity["hs_email_subject"],
										"note":data_activity["hs_email_text"],
										"user_id":data_activity["hubspot_owner_id"],
										"object_id":data_activity["hs_object_id"],
										"activity_type":activity_type
									}
								elif(activity_type == 'meeting_event_to_contact'):
									activity_data = {
										"data_deadline":data_activity["hs_timestamp"],
										"summary":data_activity["hs_meeting_body"],
										"note":data_activity["hs_meeting_body"],
										"user_id":data_activity["hubspot_owner_id"],
										"object_id":data_activity["hs_object_id"],
										"activity_type":activity_type
									}
								elif(activity_type == 'note_to_contact'):
									activity_data = {
										"data_deadline":data_activity["hs_timestamp"],
										"summary":data_activity["hs_note_body"],
										"note":data_activity["hs_note_body"],
										"user_id":data_activity["hubspot_owner_id"],
										"object_id":data_activity["hs_object_id"],
										"activity_type":activity_type
									}
								active_list.append(activity_data)
				data_list[0]["activity_data"] = json.dumps(active_list, indent=4, sort_keys=True)
		return remote_ids, data_list, kw

	def get_contact(self,custom_field_obj, id=None, **kw):
		remote_ids = []
		data_list = []
		custom_filed = custom_field_obj.mapped('hubspot_name')
		try:
			if id:
				contact = self.api.crm.contacts.basic_api.get_by_id(id, properties=CONTACT_PROPERTIES + custom_filed)
				contacts = [contact]
				activities = self.get_activities(associations_type = ["contacts"])
				kw['done'] = True
			else:
				res = self.api.crm.contacts.basic_api.get_page(
					properties=CONTACT_PROPERTIES + custom_filed,
					limit=kw['api_limit'],
					after=kw.get('next_page',0)
				)
				contacts = res.results
				activities = self.get_activities(associations_type = ["contacts"])
				paging = res.paging
				if paging:
					kw['next_page'] = paging.next.after
				else:
					kw.update(
						next_page=str(int(kw.get('next_page',0))+1),
						done=True,
					)
		except ContactApiException as e:
			raise ValueError(e.reason)
		for contact in contacts:
			properties = contact.properties
			remote_ids.append(contact.id)
			data = {
				'name': f"{properties['firstname']} {properties['lastname']}",
				'email': properties['email'],
				'phone': properties.get('phone',False),
				'city': properties.get('city',False),
				'function': properties.get('jobtitle',False),
			}

			for keys_exist in custom_field_obj:
				if(keys_exist.hubspot_name in properties):
					value = properties.get(keys_exist.hubspot_name)
					data[keys_exist.odoo_name] = value

			website = properties.get('website',False)
			if website != 'http://false':
				data['website'] = website
			association = self.api.crm.associations.batch_api.read('contact','company',
				batch_input_public_object_id={'inputs': [{'id': contact.id}]},
			)
			if association.results:
				data['parent_id'] = association.results[0].to[0].id

			data_list.append(
				{
					'remote_id': contact.id,
					'type': 'contact',
					'data': json.dumps(data, indent=4, sort_keys=True),
				}
			)

			if(activities):
				active_list = []
				for activity in activities:
					dict = activity.to_dict()
					dict_data = dict.get("results")
					for data_dict in dict_data:
						if(data_dict.get("associations") != None):
							activity_type = data_dict.get("associations",False).get("contacts",False).get("results",False)[0].get("type",False)
							if data_dict.get("associations",False).get("contacts",False).get("results",False)[0].get("id",False) == contact.id:
								data_activity = data_dict.get("properties",False)
								if(activity_type == 'call_to_contact'):
									activity_data = {
										"data_deadline":data_activity["hs_timestamp"],
										"summary":data_activity["hs_call_title"],
										"note":data_activity["hs_call_body"],
										"user_id":data_activity["hubspot_owner_id"],
										"object_id":data_activity["hs_object_id"],
										"activity_type":activity_type,
										"type": "Call"
									}
								elif(activity_type == 'email_to_contact'):
									activity_data = {
										"data_deadline":data_activity["hs_timestamp"],
										"summary":data_activity["hs_email_subject"],
										"note":data_activity["hs_email_text"],
										"user_id":data_activity["hubspot_owner_id"],
										"object_id":data_activity["hs_object_id"],
										"activity_type":activity_type,
										"type": "Email"
									}
								elif(activity_type == 'meeting_event_to_contact'):
									activity_data = {
										"data_deadline":data_activity["hs_timestamp"],
										"summary":data_activity["hs_meeting_body"],
										"note":data_activity["hs_meeting_body"],
										"user_id":data_activity["hubspot_owner_id"],
										"object_id":data_activity["hs_object_id"],
										"activity_type":activity_type,
										"type": "Meeting"
									}
								elif(activity_type == 'note_to_contact'):
									activity_data = {
										"data_deadline":data_activity["hs_timestamp"],
										"summary":data_activity["hs_note_body"],
										"note":data_activity["hs_note_body"],
										"user_id":data_activity["hubspot_owner_id"],
										"object_id":data_activity["hs_object_id"],
										"activity_type":activity_type,
										"type": "To Do"
									}
								active_list.append(activity_data)
				data_list[0]["activity_data"] = json.dumps(active_list, indent=4, sort_keys=True)

		return remote_ids, data_list, kw

	def get_deal(self,custom_field_obj, id=None, **kw):
		remote_ids = []
		data_list = []
		custom_filed = custom_field_obj.mapped('hubspot_name')
		try:
			if id:
				deal = self.api.crm.deals.basic_api.get_by_id(id, properties=DEAL_PROPERTIES + custom_filed)
				deals = [deal]
				activities = self.get_activities(associations_type = ["deal"])
				data_dict =  activities[0].to_dict()
				kw['done'] = True
			else:
				res = self.api.crm.deals.basic_api.get_page(
					properties=DEAL_PROPERTIES + custom_filed,
					limit=kw['api_limit'],
					after=kw.get('next_page',0)
				)
				activities = self.get_activities(associations_type = ["contacts"])
				deals = res.results
				paging = res.paging
				if paging:
					kw['next_page'] = paging.next.after
				else:
					kw.update(
						next_page=str(int(kw.get('next_page',0))+1),
						done=True,
					)
		except DealApiException as e:
			raise ValueError(e.reason)
		for deal in deals:
			properties = deal.properties
			remote_ids.append(deal.id)
			data = {
				'name': properties['dealname'],
				'expected_revenue': properties['amount'],
				'date_deadline': properties['closedate'],
				'stage': properties['dealstage'],
				'probability': False,
				'priority': PRIORITIES.get(properties['hs_priority'],0),
				'user_id': properties['hubspot_owner_id'],
			}

			for keys_exist in custom_field_obj:
				if(keys_exist.hubspot_name in properties):
					value = properties.get(keys_exist.hubspot_name)
					data[keys_exist.odoo_name] = value

			association = self.api.crm.associations.batch_api.read('deal','company',
				batch_input_public_object_id={'inputs': [{'id': deal.id}]},
			)
			if association.results:
				data['partner_id'] = association.results[0].to[0].id
			else:
				association = self.api.crm.associations.batch_api.read('deal','contact',
					batch_input_public_object_id={'inputs': [{'id': deal.id}]},
				)
				if association.results:
					data['partner_id'] = association.results[0].to[0].id
			associations = self.api.crm.associations.batch_api.read('deal','engagement',
				batch_input_public_object_id={'inputs': [{'id': deal.id}]},
			)
			if associations.results:
				logs = []
				for association in associations.results[0].to:
					if self.auth_type=='h_api_key':
						res = requests.get(
							url=f'https://api.hubapi.com/engagements/v1/engagements/{association.id}',
							params={'hapikey': self.api_key}
						)
					else:
						res = requests.get(
							url=f'https://api.hubapi.com/engagements/v1/engagements/{association.id}',
							headers={'Authorization': f'Bearer {self.api_key}'}
						)
					if res.ok:
						engagement = res.json()
						logs.append(
							{
								'id': str(engagement['engagement']['id']),
								'type': engagement['engagement']['type'].lower(),
								'user_id': str(engagement['engagement']['ownerId']),
								'create_date': engagement['engagement']['createdAt'],
								'subject':engagement['metadata'].get('subject'),
								'body': engagement['metadata'].get('body') or engagement['metadata'].get('html'),
							}
						)
				data['logs'] = logs
			data_list.append(
				{
					'remote_id': deal.id,
					'type': 'deal',
					'data': json.dumps(data, indent=4, sort_keys=True),
				}
			)
			if(activities):
				active_list = []
				for activity in activities:
					dict = activity.to_dict()
					dict_data = dict.get("results")
					for data_dict in dict_data:
						if(data_dict.get("associations") != None):
							activity_type = data_dict.get("associations",False).get("contacts",False).get("results",False)[0].get("type",False)
							if data_dict.get("associations",False).get("contacts",False).get("results",False)[0].get("id",False) == deal.id:
								data_activity = data_dict.get("properties",False)
								if(activity_type == 'call_to_contact'):
									activity_data = {
										"data_deadline":data_activity["hs_timestamp"],
										"summary":data_activity["hs_call_title"],
										"note":data_activity["hs_call_body"],
										"user_id":data_activity["hubspot_owner_id"],
										"object_id":data_activity["hs_object_id"],
										"activity_type":activity_type
									}
								elif(activity_type == 'email_to_contact'):
									activity_data = {
										"data_deadline":data_activity["hs_timestamp"],
										"summary":data_activity["hs_email_subject"],
										"note":data_activity["hs_email_text"],
										"user_id":data_activity["hubspot_owner_id"],
										"object_id":data_activity["hs_object_id"],
										"activity_type":activity_type
									}
								elif(activity_type == 'meeting_event_to_contact'):
									activity_data = {
										"data_deadline":data_activity["hs_timestamp"],
										"summary":data_activity["hs_meeting_body"],
										"note":data_activity["hs_meeting_body"],
										"user_id":data_activity["hubspot_owner_id"],
										"object_id":data_activity["hs_object_id"],
										"activity_type":activity_type
									}
								elif(activity_type == 'note_to_contact'):
									activity_data = {
										"data_deadline":data_activity["hs_timestamp"],
										"summary":data_activity["hs_note_body"],
										"note":data_activity["hs_note_body"],
										"user_id":data_activity["hubspot_owner_id"],
										"object_id":data_activity["hs_object_id"],
										"activity_type":activity_type
									}
								active_list.append(activity_data)
				data_list[0]["activity_data"] = json.dumps(active_list, indent=4, sort_keys=True)

		return remote_ids, data_list, kw

	def get_product(self,custom_field_obj,id=None,**kw):

		remote_ids = []
		data_list = []
		custom_filed = custom_field_obj.mapped('hubspot_name')
		try:
			if id:
				product = self.api.crm.products.basic_api.get_by_id(id, properties=PRODUCT_PROPERTIES + custom_filed)
				products = [product]
				kw['done'] = True
			else:
				res = self.api.crm.products.basic_api.get_page(
					properties=PRODUCT_PROPERTIES + custom_filed,
					limit=kw['api_limit'],
					after=kw.get('next_page',0)
				)
				products = res.results
				paging = res.paging
				if paging:
					kw['next_page'] = paging.next.after
				else:
					kw.update(
						next_page=str(int(kw.get('next_page',0))+1),
						done=True,
					)
		except ProductApiException as e:
			raise ValueError(e.reason)
		for product in products:
			properties = product.properties
			remote_ids.append(product.id)
			data = {
				'name': properties['name'],
				'default_code': properties['hs_sku'],
				'list_price': properties['price'] and float(properties['price']),
				'standard_price': properties['hs_cost_of_goods_sold'] and float(properties['hs_cost_of_goods_sold']),
				'description_sale': properties['description'],
				'type': 'consu',
			}
			for keys_exist in custom_field_obj:
				if(keys_exist.hubspot_name in properties):
					value = properties.get(keys_exist.hubspot_name)
					data[keys_exist.odoo_name] = value
			data_list.append(
				{
					'remote_id': product.id,
					'type': 'product',
					'data': json.dumps(data, indent=4, sort_keys=True),
				}
			)
		return remote_ids, data_list, kw

	def get_user(self, id=None, **kw):
		remote_ids = []
		data_list = []
		try:
			if id:
				user = self.api.crm.owners.default_api.get_by_id(id)
				users = [user]
				kw['done'] = True
			else:
				users = self.api.crm.owners.get_all()
		except UserApiException as e:
			raise ValueError(e.reason)
		for user in users:
			remote_ids.append(user.id)
			name = f"{user.first_name} {user.last_name}"
			if name == ' ':
				name = user.email
			data = {
				'name': name,
				'email':user.email,
			}
			data_list.append(
				{
					'remote_id': user.id,
					'type': 'user',
					'data': json.dumps(data, indent=4, sort_keys=True),
				}
			)
		kw['done'] = True
		return remote_ids, data_list, kw

	def post_company(self, data):
		try:
			if(data[1]):
				company = self.api.crm.companies.basic_api.create(
					simple_public_object_input_for_create={'properties': data[0]}
				)
				company_dict = company.to_dict()
				id = company_dict.get("id")
				activity_data = self.post_activities(data[1],int(id))
				activity_dict = activity_data.to_dict()
				act_id = activity_dict.get("id")
				company_dict['activity_obj_id'] = act_id
			else:
				company = self.api.crm.companies.basic_api.create(
					simple_public_object_input_for_create={'properties': data[0]}
				)
				company_dict = company.to_dict()
			return company_dict
		except CompanyApiException as e:
			raise ValueError(e.reason)

	def post_contact(self, data):
		company_id = data[0].pop('company_id',False)
		# activity_list = []
		try:
			if(data[1]):
				contact = self.api.crm.contacts.basic_api.create(
					simple_public_object_input_for_create={'properties': data[0]}
				)
				contact_dict = contact.to_dict()
				id = contact_dict.get("id")
				activity_data = self.post_activities(data[1],int(id))
				activity_dict = activity_data.to_dict()
				act_id = activity_dict.get("id")
				# activity_list.append(act_id)
				contact_dict['activity_obj_id'] = act_id
			else:
				# company_id = data[0][0].pop('company_id',False)
				contact = self.api.crm.contacts.basic_api.create(
					simple_public_object_input_for_create={'properties': data[0]}
				)
				contact_dict = contact.to_dict()
			if company_id:
				self.api.crm.associations.batch_api.create('contact','company',
					batch_input_public_association={
						'inputs': [
							{
								'from': {'id': contact.id},
								'to': {'id': company_id},
								'type': 'contact_to_company',
							}
						]
					},
				)
		except ContactApiException as e:
			raise ValueError(e.reason)
		return contact_dict

	def post_deal(self, data):
		company_id = data[0].pop('company_id',False)
		contact_id = data[0].pop('contact_id',False)
		try:
			if(data[1]):
				deal = self.api.crm.deals.basic_api.create(
					simple_public_object_input_for_create={'properties': data[0]}
				)
				deal_dict = deal.to_dict()
				id = deal_dict.get("id")
				activity_data = self.post_activities(data[1],int(id))
				activity_dict = activity_data.to_dict()
				act_id = activity_dict.get("id")
				deal_dict['activity_obj_id'] = act_id
			else:
				deal = self.api.crm.deals.basic_api.create(
					simple_public_object_input_for_create={'properties': data[0]}
				)
				deal_dict = deal.to_dict()
			if company_id:
				self.api.crm.associations.batch_api.create('deal','company',
					batch_input_public_association={
						'inputs': [
							{
								'from': {'id': deal.id},
								'to': {'id': company_id},
								'type': 'deal_to_company',
							}
						]
					},
				)
			if contact_id:
				self.api.crm.associations.batch_api.create('deal','contact',
					batch_input_public_association={
						'inputs': [
							{
								'from': {'id': deal.id},
								'to': {'id': contact_id},
								'type': 'deal_to_contact',
							}
						]
					},
				)
		except DealApiException as e:
			raise ValueError(e.reason)
		return deal_dict

	def post_product(self, data):
		try:
			product = self.api.crm.products.basic_api.create(
				simple_public_object_input_for_create={'properties': data[0]},
			)
			product_dict = product.to_dict()
		except ProductApiException as e:
			raise ValueError(e.reason)
		return product_dict

	def put_company(self, id, data):
		try:
			if(data[1][0]):
				company = self.api.crm.companies.basic_api.update(id,
					simple_public_object_input={'properties': data[0]}
				)
				company_dict = company.to_dict()
				id = company_dict.get("id")
				activity_data = self.post_activities(data[1],int(id))
				activity_dict = activity_data.to_dict()
				act_id = activity_dict.get("id")
				company_dict['activity_obj_id'] = act_id
			else:
				company = self.api.crm.companies.basic_api.update(id,
					simple_public_object_input={'properties': data[0]}
				)
				company_dict = company.to_dict()

			return company_dict
		except CompanyApiException as e:
			raise ValueError(e.reason)

	def put_contact(self, id, data):
		company_id = data[0].pop('company_id',False)
		try:
			if(data[1]):
				contact = self.api.crm.contacts.basic_api.update(id,
					simple_public_object_input={'properties': data[0]}
				)
				contact_dict = contact.to_dict()
				id = contact_dict.get("id")
				activity_data = self.post_activities(data[1],int(id))
				activity_dict = activity_data.to_dict()
				act_id = activity_dict.get("id")
				contact_dict['activity_obj_id'] = act_id
			else:
				# company_id = data.pop('company_id',False)
				contact = self.api.crm.contacts.basic_api.update(id,
					simple_public_object_input={'properties': data[0]}
				)
				contact_dict = contact.to_dict()
			if company_id:
				self.api.crm.associations.batch_api.create('contact','company',
					batch_input_public_association={
						'inputs': [
							{
								'from': {'id': contact.id},
								'to': {'id': company_id},
								'type': 'contact_to_company',
							}
						]
					},
				)
		except CompanyApiException as e:
			raise ValueError(e.reason)
		return contact_dict

	def put_deal(self, id, data):
		company_id = data[0].pop('company_id',False)
		contact_id = data[0].pop('contact_id',False)
		try:
			if(data[1]):
				deal = self.api.crm.deals.basic_api.update(id,
					simple_public_object_input={'properties': data[0]}
				)
				deal_dict = deal.to_dict()
				id = deal_dict.get("id")
				activity_data = self.post_activities(data[1],int(id))
				activity_dict = activity_data.to_dict()
				act_id = activity_dict.get("id")
				deal_dict['activity_obj_id'] = act_id
			else:
				deal = self.api.crm.deals.basic_api.update(id,
					simple_public_object_input={'properties': data[0]}
				)
				deal_dict = deal.to_dict()
			if company_id:
				self.api.crm.associations.batch_api.create('deal','company',
					batch_input_public_association={
						'inputs': [
							{
								'from': {'id': deal.id},
								'to': {'id': company_id},
								'type': 'deal_to_company',
							}
						]
					},
				)
			if contact_id:
				self.api.crm.associations.batch_api.create('deal','contact',
					batch_input_public_association={
						'inputs': [
							{
								'from': {'id': deal.id},
								'to': {'id': contact_id},
								'type': 'deal_to_contact',
							}
						]
					},
				)
		except DealApiException as e:
			raise ValueError(e.reason)
		return deal_dict

	def put_product(self, id, data):
		try:
			product = self.api.crm.products.basic_api.update(id,
				simple_public_object_input={'properties': data[0]}
			)
			product_dict = product.to_dict()
		except ProductApiException as e:
			raise ValueError(e.reason)
		return product_dict
	
	def delete_company(self, contact_id):
		try:
			response = self.api.crm.companies.basic_api.archive(int(contact_id))
		except ContactApiException as e:
			raise ValueError(e.reason)
		return response
	
	def delete_contact(self, contact_id):
		try:
			response = self.api.crm.contacts.basic_api.archive(int(contact_id))
		except ContactApiException as e:
			raise ValueError(e.reason)
		return response
	
	def delete_deal(self, contact_id):
		try:
			response = self.api.crm.deals.basic_api.archive(int(contact_id))
		except ContactApiException as e:
			raise ValueError(e.reason)
		return response
	
	def delete_product(self, contact_id):
		try:
			response = self.api.crm.products.basic_api.archive(int(contact_id))
		except ProductApiException as e:
			raise ValueError(e.reason)
		return response

	# ------------------------- Post odoo activities on hubspot ---------------------

	def post_activities(self,data,id):
		for activity_data in data:
			type = activity_data.get("type", False)
			association_type_id = activity_data.get("associationTypeId")
			if(type == "Email"):
				pop = activity_data.pop("type")
				pop = activity_data.pop("associationTypeId")
				simple_public_object_input_for_create = SimplePublicObjectInputForCreate(properties=activity_data, associations=[{"to":{"id":id},"types":[{"associationCategory":"HUBSPOT_DEFINED","associationTypeId":association_type_id}]}])
				try:
					response = self.api.crm.objects.emails.basic_api.create(simple_public_object_input_for_create=simple_public_object_input_for_create)

				except ApiException as e:
					raise ValueError(e.reason)
			
			if(type == "Meeting"):
				pop = activity_data.pop("type")
				pop = activity_data.pop("associationTypeId")
				simple_public_object_input_for_create = SimplePublicObjectInputForCreate(properties=activity_data, associations=[{"to":{"id":id},"types":[{"associationCategory":"HUBSPOT_DEFINED","associationTypeId":association_type_id}]}])
				try:
					response = self.api.crm.objects.meetings.basic_api.create(simple_public_object_input_for_create=simple_public_object_input_for_create)
				except ApiException as e:
					raise ValueError(e.reason)
				
			if(type == "Call"):
				pop = activity_data.pop("type")
				pop = activity_data.pop("associationTypeId")
				simple_public_object_input_for_create = SimplePublicObjectInputForCreate(properties=activity_data, associations=[{"to":{"id":id},"types":[{"associationCategory":"HUBSPOT_DEFINED","associationTypeId":association_type_id}]}])
				try:
					response = self.api.crm.objects.calls.basic_api.create(simple_public_object_input_for_create=simple_public_object_input_for_create)
				except ApiException as e:
					raise ValueError(e.reason)
				
			if(type == "To-Do"):
				pop = activity_data.pop("type")
				pop = activity_data.pop("associationTypeId")
				simple_public_object_input_for_create = SimplePublicObjectInputForCreate(properties=activity_data, associations=[{"to":{"id":id},"types":[{"associationCategory":"HUBSPOT_DEFINED","associationTypeId":association_type_id}]}])
				try:
					response = self.api.crm.objects.notes.basic_api.create(simple_public_object_input_for_create=simple_public_object_input_for_create)

				except ApiException as e:
					raise ValueError(e.reason)
		return response
	
	# ------------------------- Geting Hubspot Activites data for creating activites on odoo ---------------------

	def get_activities(self,associations_type):

		# For call activity
		try:
			response_call = self.api.crm.objects.calls.basic_api.get_page(limit=10, properties=CALL_ACTIVIY, associations=associations_type, archived=False)
			
		except ApiException as e:
				raise ValueError(e.reason)
		
		# For email activity

		try:
			response_email = self.api.crm.objects.emails.basic_api.get_page(limit=10, properties=EMAIL_ACTIVIY, associations=associations_type, archived=False)
		except ApiException as e:
				raise ValueError(e.reason)

		# For meeting activity

		try:
			response_meeting = self.api.crm.objects.meetings.basic_api.get_page(limit=10, properties=MEETING_ACTIVIY, associations=associations_type, archived=False)
		except ApiException as e:
				raise ValueError(e.reason)

		# For To do activity

		try:
			response_note = self.api.crm.objects.notes.basic_api.get_page(limit=10, properties=NOTE_ACTIVIY, associations=associations_type, archived=False)
		except ApiException as e:
				raise ValueError(e.reason)

		return response_call,response_email,response_meeting,response_note
	
	def put_activities(self,obj_id, activity_type):
		response = False
		if activity_type == "Meeting":
			updated_meeting_data = {
				"hs_meeting_outcome": "SCHEDULED"
			}
			try:
				response = self.api.crm.objects.meetings.basic_api.update(obj_id, simple_public_object_input={'properties': updated_meeting_data})
			except ApiException as e:
				raise ValueError(e.reason)
		
		if activity_type == "Call":
			updated_call_data = {
				"hs_call_status": "CONNECTING"
			}
			try:
				response = self.api.crm.objects.calls.basic_api.update(obj_id, simple_public_object_input={'properties': updated_call_data})
			except ApiException as e:
				raise ValueError(e.reason)

		return response
	
if __name__ == '__main__':
	API_KEY = '9931e5a4-6b80-493e-9aa4-dfa335ea226f'
	with Bridge(API_KEY) as bridge:
		# res = bridge.get_contact()
		# res = bridge.post_contact({"email": "email@example.com"})
		# res = bridge.get_contact(201)
		# res = bridge.put_contact(101, {"firstname": "first_name"})
		# res = bridge.get_pipline_stage()
		# res = bridge.get_deal(5408027187)
		res = bridge.get_product()
	print(res)
