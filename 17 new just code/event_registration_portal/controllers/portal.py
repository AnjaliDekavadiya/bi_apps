# -*- coding: utf-8 -*-


from collections import OrderedDict
import werkzeug

import base64
from odoo import http, _
from odoo.http import request
from odoo import models,registry, SUPERUSER_ID
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager

from odoo.osv.expression import OR

class CustomerPortal(CustomerPortal):
    _items_per_page = 10

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
 
        EventRegi = request.env['event.registration']
        custom_event_count = EventRegi.sudo().search_count([
            ('partner_id', 'child_of', [partner.commercial_partner_id.id])
        ])
        values.update({
            'custom_event_count': custom_event_count,
        })
        return values

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        values['custom_event_count'] = request.env['event.registration'].sudo().search_count([
            ('partner_id','child_of',[request.env.user.commercial_partner_id.id])
        ])
        return values

    #
    # Event Registration
    #

    @http.route(['/my/event_custom_lists', '/my/event_custom_lists/page/<int:page>'], type='http', auth="user", website=True)
    # def portal_my_events(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='content', **kw):
    def portal_my_events(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='all', **kw):

        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        event_obj = http.request.env['event.registration']
        domain = [
            ('partner_id', 'child_of', [partner.commercial_partner_id.id])
        ]
        # count for pager
        custom_event_count = event_obj.sudo().search_count(domain)
        # pager
        # pager = request.website.pager(
        #     url="/my/event_custom_lists",
        #     total=custom_event_count,
        #     page=page,
        #     step=self._items_per_page
        # )
        pager = portal_pager(
            url="/my/event_custom_lists",
            total=custom_event_count,
            page=page,
            step=self._items_per_page
        )
        searchbar_sortings = {
            'create_date': {'label': _('Newest'), 'order': 'create_date desc'},
            'state': {'label': _('State'), 'order': 'state'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }
        searchbar_inputs = {
            'title': {'input': 'title', 'label': _('Search (in Event)')},
            'create_date': {'input': 'create_date', 'label': _('Search in date')},
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
            if search_in in ('stage', 'all'):
                search_domain = OR([search_domain, [('state', 'ilike', search)]])
            domain += search_domain

        # content according to pager and archive selected
        events = event_obj.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'events': events,
            'page_name': 'event_custom_page',
            'pager': pager,
            'default_url': '/my/event_custom_lists',
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("event_registration_portal.portal_my_event_registrationcustom", values)

    @http.route(['/my/event_custom/<model("event.registration"):event>'], type='http', auth="user", website=True)
    def my_event(self, event, access_token=None, **kw):
        event_obj = http.request.env['event.registration'].sudo().browse(event.id)
        partner = request.env.user.partner_id
        if partner.commercial_partner_id.id != event_obj.partner_id.commercial_partner_id.id:
           return request.redirect("/")
        return request.render("event_registration_portal.display_event_custom", {'event': event, 'user': request.env.user})


    