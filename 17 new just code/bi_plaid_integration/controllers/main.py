# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
from odoo import http

from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from odoo.http import request


class PlaidIntegration(http.Controller):

	@http.route(["/create_link_token"], type="http", auth='user', methods=['POST'], csrf=False, save_session=False)
	def create_link_token(self):
		bi_plaid_bank_obj = request.env['bi.plaid.bank.details']

		link_token_request = LinkTokenCreateRequest(
			products=[Products("transactions")],
			client_name="Plaid Test App",
			country_codes=[CountryCode('US')],
			language='en',
			user=LinkTokenCreateRequestUser(
				client_user_id='test_client_user_id'
			)
		)
		client = bi_plaid_bank_obj.get_plaid_configuration()
		response = client.link_token_create(link_token_request)
		return response.to_dict()['link_token']

	@http.route(["/exchange_public_token"], type="http", methods=['POST'], auth="user", csrf=False, save_session=False)
	def ExchangePublicToken(self, **kw):
		bi_plaid_bank_obj = request.env['bi.plaid.bank.details']

		public_token = request.params['public_token']
		item_token_exchange_request = ItemPublicTokenExchangeRequest(
			public_token=public_token
		)
		client = bi_plaid_bank_obj.get_plaid_configuration()
		response = client.item_public_token_exchange(item_token_exchange_request)
		if response and response.get('access_token'):
			request.env['ir.config_parameter'].sudo().set_param(
				'bi_plaid_integration.bi_plaid_access_token', response.get('access_token'))
		return json.dumps({'public_token_exchange': 'complete'})

	@http.route(["/create_plaid_account"], type="http", methods=['POST'], auth="user", csrf=False, save_session=False)
	def create_plaid_account(self, **kw):
		bi_plaid_bank_obj = request.env['bi.plaid.bank.details']
		bank_id = request.params['bank_id']
		bi_plaid_bank_obj.get_plaid_account_details(bank_id)

		return json.dumps({})
