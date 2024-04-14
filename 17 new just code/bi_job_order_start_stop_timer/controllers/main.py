# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


import werkzeug
import json
import base64

import odoo.http as http
from odoo.http import request
from odoo.exceptions import AccessError, MissingError
from odoo.addons.portal.controllers.portal import get_records_pager,CustomerPortal, pager as portal_pager
import odoo.http as http

class Getdata(http.Controller):

	@http.route('/load_data', type='json', auth='user', methods=['POST'])
	def get_data(self,  **post):
		if post['job_data'] in post:
			job_ids = request.env['job.order'].sudo().browse(post['job_data'])
			values = {'job_ids':job_ids}
			return values

	@http.route('/load_order', type='json', auth='user', methods=['POST'],website=True)
	def get_job(self, **post):
		timedetails = post['time_details']
		job_order = post['job_order']
		if post['task_name']:
			task_object = request.env['project.task'].search([('id', '=', post['task_name'])])
			employee_object = request.env['hr.employee'].search([('user_id', '=', request.env.user.id)])
			project_object = request.env['project.project'].search([('id', '=', task_object.project_id.id)])
			job_object = request.env['job.order'].search([('id', '=',job_order), ('project_id', '=', project_object.id)])
			for dict_line in timedetails:
				product_dict = dict_line.get('time_details')
				vals = {
					'date': post['date'],
					'project_id': project_object.id,
					'task_id': task_object.id,
					'employee_id': employee_object.id,
					'st_time': product_dict.get('last_start_time'),
					'ed_time': product_dict.get('last_stop_time'),
					'name': 'this time sheet for job order',
					'unit_amount': product_dict.get('total_duration'),
					'account_analytic_line_id': job_object.id
				}
				timesheet = job_object.timesheet_ids.create(vals)
			return timesheet.id
		else:
			task_object = self.env['project.task'].search([('id', '=', post['task_name'])])
			employee_object = self.env['hr.employee'].search([('user_id', '=', request.env.user.id)])
			project_object = self.env['project.project'].search([('id', '=', task_object.project_id.id)])
			job_object = self.env['job.order'].search([('id', '=', job_order), ('project_id', '=', project_object.id)])
			for dict_line in timedetails:
				product_dict = dict_line.get('time_details')
				vals = {
					'date': post['date'],
					'project_id': project_object.id,
					'task_id': task_object.id,
					'employee_id': employee_object.id,
					'st_time': product_dict.get('last_start_time'),
					'ed_time': product_dict.get('last_stop_time'),
					'name': 'this time sheet for job order',
					'unit_amount': product_dict.get('total_duration'),
					'account_analytic_line_id': job_object.id
				}
				timesheet = job_object.timesheet_ids.create(vals)
			return timesheet.id


class WebsiteJobOrder(CustomerPortal):

	def _prepare_home_portal_values(self, counters):
		values = super()._prepare_home_portal_values(counters)
		if 'job_order_count' in counters:
			job_order_obj = request.env['job.order']
			job_order_count = job_order_obj.search_count([])

			values.update({
				'job_order_count': job_order_count,
			})
		return values

	def _prepare_portal_layout_values(self):
		values = super(WebsiteJobOrder, self)._prepare_portal_layout_values()
		partner = request.env.user.partner_id

		job_order_obj = request.env['job.order']
		job_order_count = job_order_obj.search_count([])

		values.update({
			'job_order_count': job_order_count,
		})
		return values



	@http.route(['/my/job_order', '/my/job_order/page/<int:page>'], type='http', auth="user", website=True)
	def portal_job_order_list(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
		values = self._prepare_portal_layout_values()
		partner = request.env.user.partner_id
		job_order = request.env['job.order']

		domain = []
		# count for pager
		repair_count = job_order.search_count(domain)
		# make pager
		pager = request.website.pager(
			url="/my/job_order",
			total=repair_count,
			page=page,
			step=self._items_per_page
		)
		# search the count to display, according to the pager data
		partner = request.env.user.partner_id
		job = job_order.search([])
		
		values.update({
			'job': job,
			'page_name': 'job_order',
			'pager': pager,
			'default_url': '/my/job_order',
		})
		
		return request.render("bi_job_order_start_stop_timer.portal_job_order_list", values)



	@http.route(['/job/view/detail/<model("job.order"):job>'],type='http',auth="public",website=True)
	def job_view(self, job, category='', search='', **kwargs):
		
		context = dict(request.env.context or {})
		job_obj = request.env['job.order']
		context.update(active_id=job.id)
		job_data_list = []
		job_data = job_obj.browse(int(job))
		for items in job_data:
			job_data_list.append(items)
		if request.website:
			website = request.website.write({'job_order_id': job.id})
		return http.request.render('bi_job_order_start_stop_timer.job_order_request_view',{
			'job_data_list': job,
		}) 

	@http.route(['/my/task/accept'], type='json', auth="public", website=True)
	def portal_quote_accept(self, res_id=None, access_token=None, partner_name=None, signature=None, **kwargs):
		order = request.env['job.order'].search([('id','=',request.website.job_order_id)])
		vals = {'digital_signature':signature}
		order.write(vals)
		return order

	@http.route(['/my/tasks/<int:task_id>'], type='http', auth="user", website=True)
	def portal_my_task(self, task_id, report_type=None, access_token=None, project_sharing=False, **kw):
		val = (request.httprequest.__dict__)
		array = val.get('environ').get('HTTP_REFERER').split('/')
		array2 = val.get('environ').get('HTTP_REFERER').split('/')[len(array) - 1].split('-')
		property_url_id = array2[len(array2) - 1]
		task = request.env['project.task'].browse(task_id)
		project = request.env['project.project'].search([('task_ids', 'in', task_id)])
		job_order = request.env['job.order'].search([('id', '=', property_url_id)])
		try:
			task_sudo = self._document_check_access('project.task', task_id, access_token)
		except (AccessError, MissingError):
			return request.redirect('/my')

		if report_type in ('pdf', 'html', 'text'):
			return self._show_task_report(task_sudo, report_type, download=kw.get('download'))

		# ensure attachment are accessible with access token inside template
		for attachment in task_sudo.attachment_ids:
			attachment.generate_access_token()
		if project_sharing is True:
			# Then the user arrives to the stat button shown in form view of project.task and the portal user can see only 1 task
			# so the history should be reset.
			request.session['my_tasks_history'] = task_sudo.ids

		values = self._task_get_page_view_values(task_sudo, access_token, **kw)
		values.update({
			'task': task,
			'job_order': job_order,
			'user': request.env.user
		})
		history = request.session.get('my_tasks_history', [])
		values.update(get_records_pager(history, task))
		values.update({'job_order': job_order})
		return request.render("bi_job_order_start_stop_timer.task_order_request_view", values)


class EditTimesheet(http.Controller):

	# SAVE EDITED TIMESHEET
	@http.route(['/my/save_edit_timesheet'], type='http', auth="public", website=True)
	def edit_timesheet_save(self,context=None,**post):
		if post:
			project = post['project']
			task = post['task']
			date = post['date']
			duration = post['duration']
			st_time = post['st_time']
			ed_time = post['ed_time']
			work_type = post['work_types']
			disc = post['disc']
			is_billable = post.get('is_billable') or False
			is_paid = post.get('is_paid') or False

		if is_billable == 'on':
			is_billable = True
		else:
			is_billable = False

		if is_paid == 'on':
			is_paid = True
		else:
			is_paid = False

		timesheet_id = str(post['timesheet_id'])

		project_obj = request.env['project.project'].sudo().search([('id','=',project)])
		task_obj = request.env['project.task'].sudo().search([('id','=',task)])
		analytic_obj = request.env['account.analytic.line'].sudo().search([('id','=',timesheet_id)])
		work_type = request.env['timesheet.work.type'].sudo().search([('work_type','ilike',work_type)])
		duration_replace = duration.replace(':', '.')
		analytic_obj.update({
			'date':date,
			'user_id': request.env.user.id,
			'name': disc,
			'project_id': project_obj.id,
			'task_id': task_obj.id,
			'work_type': work_type.id,
			'st_time': st_time,
			'ed_time': ed_time,
			'is_billable': is_billable,
			'is_paid': is_paid,
			'unit_amount': float(duration_replace),
			'employee': request.env.user.id, 
		})
		return request.redirect("/my/timesheet")

