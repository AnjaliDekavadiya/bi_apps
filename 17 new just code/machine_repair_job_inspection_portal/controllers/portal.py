# -*- coding: utf-8 -*-


from collections import OrderedDict
import werkzeug

import base64
from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError, MissingError
from odoo import models,registry, SUPERUSER_ID
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager

from odoo.osv.expression import OR

class CustomerPortal(CustomerPortal):
    _items_per_page = 10

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'custom_machine_inspection_count' in counters:
            partner = request.env.user.partner_id
            custom_machine_inspection_count = request.env['repair.order.inspection'].search_count([('custom_inspector_ids', 'child_of', [partner.commercial_partner_id.id])])
            values['custom_machine_inspection_count'] = custom_machine_inspection_count
            print('-------------values------',values)

        return values

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
 
        MachineJobInspection = request.env['repair.order.inspection']
        custom_machine_inspection_count = MachineJobInspection.sudo().search_count([
            ('custom_inspector_ids', 'child_of', [partner.commercial_partner_id.id])
        ])
        values.update({
            'custom_machine_inspection_count': custom_machine_inspection_count,
        })
        return values

    def _inspection_get_page_view_values(self, machine_inspection, access_token, **kwargs):
        values = {
            'page_name': 'machine_inspection_custom_page',
            'machine_inspection': machine_inspection,
        }
        return self._get_page_view_values(machine_inspection, access_token, values, 'my_machine_inspection_history', False, **kwargs)

    @http.route(['/my/custom_machine_inspection_list', '/my/custom_machine_inspection_list/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_machine_inspection_custom(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='all', **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        inspection_obj = http.request.env['repair.order.inspection']
        domain = [
            ('custom_inspector_ids', 'child_of', [partner.commercial_partner_id.id])
        ]
        # count for pager
        custom_machine_inspection_count = inspection_obj.sudo().search_count(domain)
        # pager
       
        pager = portal_pager(
            url="/my/custom_machine_inspection_list",
            total=custom_machine_inspection_count,
            page=page,
            step=self._items_per_page
        )
        searchbar_sortings = {
            'create_date': {'label': _('Newest'), 'order': 'create_date desc'},
        }

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }
        searchbar_inputs = {
            # 'title': {'input': 'title', 'label': _('Search <span class="nolabel"> (in Machine Inspection)</span>')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        # default sort by value
        if not sortby:
            sortby = 'create_date'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']


        # search
        if search and search_in:
            search_domain = []
            if search_in in ('create_date', 'all'):
                search_domain = OR([search_domain, [('create_date', 'ilike', search)]])
            if search_in in ('state', 'all'):
                search_domain = OR([search_domain, [('state', 'ilike', search)]])
            domain += search_domain

        # content according to pager and archive selected
        machine_inspections = inspection_obj.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'machine_inspections': machine_inspections,
            'page_name': 'machine_inspection_custom_page',
            'pager': pager,
            'default_url': '/my/custom_machine_inspection_list',
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("machine_repair_job_inspection_portal.portal_my_machine_inspection_customs", values)

    @http.route(['/my/machine_inspection_custom/<model("repair.order.inspection"):machine_inspection>'], type='http', auth="user", website=True)
    def custom_portal_my_machine_inspections(self, machine_inspection=None, access_token=None, **kw):
        inspection_obj = http.request.env['repair.order.inspection'].sudo().browse(machine_inspection.id)
        values = self._inspection_get_page_view_values(inspection_obj, access_token, **kw)
        return request.render("machine_repair_job_inspection_portal.display_machine_job_inspections_custom", values)

