# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


import werkzeug
import json
import base64

import odoo.http as http
from odoo.http import request
from odoo import SUPERUSER_ID, _
from datetime import datetime, timedelta, time
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
import odoo.http as http
from odoo.osv.expression import OR


class WebsiteIssueRequest(CustomerPortal):

	@http.route(['/issue_request/message'],type='http',auth="public",website=True)
	def issue_request_message(self, **post):
		Attachments = request.env['ir.attachment']
		upload_file = post['upload']
		if ',' in post.get('issue_id'):
			bcd = post.get('issue_id').split(',')
		else : 
			bcd = [post.get('issue_id')]
			
		issue_request_obj = request.env['project.issue'].sudo().search([('id','in',bcd)]) 
			
		if upload_file:
			attachment_id = Attachments.sudo().create({
				'name': upload_file.filename,
				'type': 'binary',
				'datas': base64.encodebytes(upload_file.read()),
				'datas_fname': upload_file.filename,
				'public': True,
				'res_model': 'ir.ui.view',
				'proj_issue_id' : issue_request_obj.id,
			})
		
		context = dict(request.env.context or {})
		issue_request_obj = request.env['project.issue']
					
		return http.request.render('bi_construction_contracting_issue_tracking.issue_message_thank_you') 
