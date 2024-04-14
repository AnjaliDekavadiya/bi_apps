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

	@http.route('/issue_request', type="http", auth="public", website=True)
	def issue_request_request(self, **kw):
		"""Let's public and registered user submit a Issue Request"""
		name = ""
		if http.request.env.user.name != "Public user":
			name = http.request.env.user.name
			
		email = http.request.env.user.partner_id.email
		phone = http.request.env.user.partner_id.phone
		values = {'user_ids': name,'email':email,'phone':phone}
		
		return http.request.render('bi_construction_contracting_issue_tracking.bi_create_issue_request', values)

	@http.route('/issue_request/thankyou', type="http", auth="public", website=True)
	def issue_request_thankyou(self, **post):
		"""Displays a thank you page after the user submit a Issue Request"""
		if post.get('debug') or not post:
			return request.render("bi_construction_contracting_issue_tracking.issue_request_request_thank_you")

		user_brw = request.env['res.users'].sudo().browse(request.uid)
		Attachments = request.env['ir.attachment']
		upload_file = post['upload']

		
		vals = {
					'name' : post['subject'],
					'partner_id' : user_brw.partner_id.id,
					'user_id' : user_brw.id,
					'email_from' : post['email_from'],
					'phone' : post['phone'],
					'company_id' : user_brw.company_id.id or False,
					'date_create' : datetime.now(),
					'priority' : post['priority'],
					'category_id' : int(post['category']),
					'project_id' : int(post['project_id']),
					'description' : post['description'],
			}
		issue_req_obj = request.env['project.issue'].sudo().create(vals)
		
		if upload_file:
			attachment_id = Attachments.sudo().create({
				'name': upload_file.filename,
				'type': 'binary',
				'datas': base64.encodebytes(upload_file.read()),
				'public': True,
				'res_model': 'ir.ui.view',
				'proj_issue_id' : issue_req_obj.id,
			}) 
		values = {'issue_id': issue_req_obj.sequence,}
		return request.render("bi_construction_contracting_issue_tracking.issue_request_request_thank_you",values)  

	def _prepare_portal_layout_values(self):
		values = super(WebsiteIssueRequest, self)._prepare_portal_layout_values()
		partner = request.env.user.partner_id
		issue_req = request.env['project.issue']
		partner_issue_req_count = issue_req.sudo().search([('partner_id','=',partner.id)])
		issue_count =issue_req.sudo().search_count([('partner_id','=',partner.id)])

		values.update({
			'issue_count': issue_count,
		})
		return values  
		
	@http.route(['/my/issue_request', '/my/issue_request/page/<int:page>'], type='http', auth="user", website=True)
	def portal_my_issue_req(self, page=1, date_begin=None,search=None, search_in='content', date_end=None, sortby=None, **kw):
		values = self._prepare_portal_layout_values()
		partner = request.env.user.partner_id
		issue_request = request.env['project.issue']

		domain = []


		if date_begin and date_end:
			domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
		

		searchbar_sortings = {
			'sequence': {'label': _('Order By Sequence Desc'), 'order': 'sequence desc'},
			'date': {'label': _('Order By Date Desc'), 'order': 'date_create desc'},
			'issue': {'label': _('Order By Name Desc'), 'order': 'name desc'},
			'sequence1': {'label': _('Order By Sequence Asc'), 'order': 'sequence'},
			'date1': {'label': _('Order By Date Asc'), 'order': 'date_create '},
			'issue1': {'label': _('Order By Name Asc'), 'order': 'name '},
		}

		searchbar_inputs = {
			'issue': {'input': 'name', 'label': _('Search in Name')},
			'sequence': {'input': 'sequence', 'label': _('Search in Sequence Number')},
		}


		if not sortby:
			sortby = 'issue'
		sort_note = searchbar_sortings[sortby]['order']

		if search and search_in:
			search_domain = []
			if search_in in ('name', 'all'):
				search_domain = OR([search_domain, [('name', 'ilike', search)]])
			if search_in in ('sequence', 'all'):
				search_domain = OR([search_domain, [('sequence', 'ilike', search)]])
			domain += search_domain

		# count for pager
		issue_count = issue_request.sudo().search_count(domain)

		# make pager
		pager = request.website.pager(
			url="/my/issue_request",
			url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
			total=issue_count,
			page=page,
			step=self._items_per_page
		)

		# search the count to display, according to the pager data
		partner = request.env.user.partner_id
		domain += [('partner_id','=',partner.id)]
		issue = issue_request.sudo().search(domain,order=sort_note, limit=self._items_per_page, offset=pager['offset'])
		

		values.update({
			'issue': issue,
			'page_name': 'issue_request',
			'pager': pager,
			'default_url': '/my/issue_request',
			'date': date_begin,
			'searchbar_sortings': searchbar_sortings,
			'searchbar_inputs': searchbar_inputs,
			'search_in': search_in,
			'sortby': sortby,
		})
		
		return request.render("bi_construction_contracting_issue_tracking.portal_my_issue_req", values)

	@http.route(['/issue/view/detail/<model("project.issue"):issue>'],type='http',auth="public",website=True)
	def issue_view(self, issue, category='', search='', **kwargs):
		
		context = dict(request.env.context or {})
		issue_obj = request.env['project.issue']
		context.update(active_id=issue.id)
		issue_data_list = []
		issue_data = issue_obj.sudo().browse(int(issue))
		
		for items in issue_data:
			issue_data_list.append(items)
			
		return http.request.render('bi_construction_contracting_issue_tracking.issue_request_request_view',{
			'issue_data_list': issue
		}) 


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
				'public': True,
				'res_model': 'ir.ui.view',
				'proj_issue_id' : issue_request_obj.id,
			})
		
		context = dict(request.env.context or {})
		issue_request_obj = request.env['project.issue']
		if post.get( 'message' ):
			message_id1 = request.env['project.issue'].my_message_post(
				post.get( 'message' ),
				post.get('issue_id'),
				type='comment',
				subtype='mt_comment')
				
			message_id1.body = post.get( 'message' )
			message_id1.type = 'comment'
			message_id1.subtype = 'mt_comment'
			message_id1.model = 'project.issue'
			message_id1.res_id = post.get( 'issue_id' )
					
		return http.request.render('bi_construction_contracting_issue_tracking.issue_message_thank_you') 
		
	@http.route(['/issue/comment/<model("project.issue"):issue>'],type='http',auth="public",website=True)
	def issue_comment_page(self, issue,**post):  
		
		return http.request.render('bi_construction_contracting_issue_tracking.issue_request_comment',{'issue': issue}) 
	 
	@http.route(['/issue_request/comment/send'],type='http',auth="public",website=True)
	def issue_request_comment(self, **post):
		
		context = dict(request.env.context or {})
		if post.get('issue_id'):

			issue_request_obj = request.env['project.issue'].sudo().browse(int(post['issue_id']))
			if post.get('customer_rating'):
				issue_request_obj.update({
						'customer_rating' : post['customer_rating'],            
						'comment' : post['comment'],
				})
			else:
				issue_request_obj.update({
						'customer_rating' :'',            
						'comment' : post['comment'],
				})
		return http.request.render('bi_construction_contracting_issue_tracking.issue_request_rating_thank_you')           
				

			   
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:        
