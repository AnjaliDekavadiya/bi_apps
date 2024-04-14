# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import OrderedDict
from operator import itemgetter

from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import groupby as groupbyelem

from odoo.osv.expression import OR

import logging
_logger = logging.getLogger(__name__)

class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'custom_issues_count' in counters:
            values['custom_issues_count'] = request.env['project.task'].with_context({'is_custom_bugs': True}).search_count([('custom_type', '=', 'bugs_issues'),('partner_id','child_of',[request.env.user.partner_id.commercial_partner_id.id])])
        return values

    # def _prepare_portal_layout_values(self):
    #     values = super(CustomerPortal, self)._prepare_portal_layout_values()
    #     values['custom_issues_count'] = request.env['project.task'].with_context({'is_custom_bugs': True}).search_count([('custom_type', '=', 'bugs_issues'),('partner_id','child_of',[request.env.user.partner_id.commercial_partner_id.id])])
    #     return values

    # ---------------------------------------------------------
    # My Project Issues
    # ------------------------------------------------------------
    def custom_project_issue_get_page_view_values(self, task, access_token, **kwargs):
        values = {
            'page_name': 'project_issues',
            'cust_project_issue': task,
            'user': request.env.user
        }
        return self._get_page_view_values(task, access_token, values, 'my_tasks_history', False, **kwargs)

    @http.route(['/my/project/custom_issues', '/my/project/custom_issues/page/<int:page>'], type='http', auth="user", website=True)
    def custom_portal_my_project_issues(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='content', groupby='project', **kw):
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Title'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'stage_id'},
            'update': {'label': _('Last Stage Update'), 'order': 'date_last_stage_update desc'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }
        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Search <span class="nolabel"> (in Content)</span>')},
            'message': {'input': 'message', 'label': _('Search in Messages')},
            'customer': {'input': 'customer', 'label': _('Search in Customer')},
            'stage': {'input': 'stage', 'label': _('Search in Stages')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'project': {'input': 'project', 'label': _('Project')},
        }

        # extends filterby criteria with project the customer has access to
        projects = request.env['project.project'].search([])
        for project in projects:
            searchbar_filters.update({
                str(project.id): {'label': project.name, 'domain': [('project_id', '=', project.id)]}
            })

        # extends filterby criteria with project (criteria name is the project id)
        # Note: portal users can't view projects they don't follow
        project_groups = request.env['project.task'].with_context({'is_custom_bugs': True}).read_group([('custom_type', '=', 'bugs_issues'), ('project_id', 'not in', projects.ids)],
                                                                ['project_id'], ['project_id'])
        for group in project_groups:
            proj_id = group['project_id'][0] if group['project_id'] else False
            proj_name = group['project_id'][1] if group['project_id'] else _('Others')
            searchbar_filters.update({
                str(proj_id): {'label': proj_name, 'domain': [('project_id', '=', proj_id)]}
            })

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters[filterby]['domain']

        # archive groups - Default Group By 'create_date'
        # archive_groups = self._get_archive_groups('project.task', domain) #odoo14
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('content', 'all'):
                search_domain = OR([search_domain, ['|', ('name', 'ilike', search), ('description', 'ilike', search)]])
            if search_in in ('customer', 'all'):
                search_domain = OR([search_domain, [('partner_id', 'ilike', search)]])
            if search_in in ('message', 'all'):
                search_domain = OR([search_domain, [('message_ids.body', 'ilike', search)]])
            if search_in in ('stage', 'all'):
                search_domain = OR([search_domain, [('stage_id', 'ilike', search)]])
            domain += search_domain

        domain += [('custom_type', '=', 'bugs_issues'),('partner_id','child_of',[request.env.user.partner_id.commercial_partner_id.id])]

        # task count
        task_count = request.env['project.task'].with_context({'is_custom_bugs': True}).search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/project/custom_issues",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby, 'search_in': search_in, 'search': search},
            total=task_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        if groupby == 'project':
            order = "project_id, %s" % order  # force sort on project first to group by project in view
        tasks = request.env['project.task'].with_context({'is_custom_bugs': True}).search(domain, order=order, limit=self._items_per_page, offset=(page - 1) * self._items_per_page)
        request.session['my_tasks_history'] = tasks.ids[:100]
        if groupby == 'project':
            grouped_tasks = [request.env['project.task'].concat(*g) for k, g in groupbyelem(tasks, itemgetter('project_id'))]
        else:
            grouped_tasks = [tasks]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_tasks': grouped_tasks,
            'page_name': 'project_issues',
            # 'archive_groups': archive_groups, #odoo14
            'default_url': '/my/project/custom_issues',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("project_bugs_issue_management.custom_portal_my_project_issues", values)

    @http.route(['/my/project/custom_issues/<int:task_id>'], type='http', auth="public", website=True)
    def custom_portal_my_project_issue(self, task_id, access_token=None, **kw):
        task = request.env['project.task'].sudo().browse(int(task_id))
        try:
            #task_sudo = self._document_check_access('project.task', task_id, access_token)
            if task.partner_id.commercial_partner_id.id == request.env.user.partner_id.commercial_partner_id.id:
                task_sudo = task
            else:
                return request.redirect('/my')
        except (AccessError, MissingError):
            return request.redirect('/my')

        # ensure attachment are accessible with access token inside template
        for attachment in task_sudo.attachment_ids:
            attachment.generate_access_token()
        values = self.custom_project_issue_get_page_view_values(task_sudo, access_token, **kw)
        return request.render("project_bugs_issue_management.custom_portal_my_project_issue", values)

    @http.route(['/my/issues/create/<int:task_id>'], type='http', auth="public", website=True)
    def custom_portal_my_project_issue_create(self, task_id, access_token=None,**kw):
        try:
            task_sudo = self._document_check_access('project.task', task_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = {
            'page_name': 'issue_create',
            'issue_task': task_sudo,
            'user': request.env.user,
            'types': request.env['custom.issues.type'].sudo().search([]),
        }
        return request.render("project_bugs_issue_management.custom_project_issue_create_template", values)

    @http.route(['/my/issues/create'], type='http', auth="public", website=True)
    def custom_portal_my_issue_create(self, **kw):
        values = {
            'custom_type': 'bugs_issues',
            'custom_repoter_id': request.env.user.id,
        }
        task_id = False
        project_id = False
        if kw.get('task', False):
            task_id = request.env['project.task'].sudo().browse(int(kw.get('task')))
            values.update({'custom_task_id': task_id.id})
        if task_id and task_id.project_id:
            project_id = task_id.project_id
            values.update({'project_id': task_id.project_id.id})
        if kw.get('name', ''):
            values.update({'name': str(kw.get('name'))})
        if kw.get('issue_type_id', False):
            values.update({'custom_issues_type_id': int(kw.get('issue_type_id'))})
        if kw.get('description', ''):
            values.update({'description': str(kw.get('description'))})
        if kw.get('environment', ''):
            values.update({'custom_environment': str(kw.get('environment'))})
        new_task_id = request.env['project.task'].sudo().create(values)
        values = {
            'new_task_id': new_task_id,
        }
        if new_task_id:
            return request.render("project_bugs_issue_management.custom_issue_successfully_created_message", values)
        else:
            return request.render("portal.portal_my_home")