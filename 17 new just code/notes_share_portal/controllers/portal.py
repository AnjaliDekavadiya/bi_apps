# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.osv.expression import OR



class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super(CustomerPortal, self)._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        custom_notes_ids = request.env['project.task'].sudo().search_count([
            ('custom_partner_ids', 'child_of', [partner.commercial_partner_id.id])
        ])

        values.update({
        'custom_notes_count': custom_notes_ids,
        })
        return values

    def custom_note_get_page_view_values(self, note, access_token, **kwargs):
        values = {
            'page_name': 'custom_note',
            'note': note.sudo(),
            'token': access_token,
            'bootstrap_formatting': True,
        }
        return values


    @http.route(['/my/custom_notes_list_view', '/my/custom_notes_list_view/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_note_custom_list_view(self, page=1, search=None, search_in='name', **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        note_obj = request.env['project.task']

        domain = [
            ('custom_partner_ids' , 'child_of', [partner.commercial_partner_id.id])
        ]

        searchbar_inputs = {
            'name': {'input': 'name', 'label': _('Search in Notes')},
            'tag_ids': {'input': 'tag_ids', 'label': _('Search in Tags')},
        }
        if search and search_in:
            search_domain = []
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            if search_in in ('tag_ids', 'all'):
                search_domain = OR([search_domain, [('tag_ids', 'ilike', search)]])
            domain += search_domain
       
        # count for pager
        notes_count = note_obj.search_count(domain) 
        # make pager
        pager =  request.website.pager(
            url="/my/custom_notes_list_view",
            url_args={'search_in': search_in, 'search': search},
            total=notes_count,
            page=page,
            step=self._items_per_page
        )

        # search the count to display, according to the pager data
        notes = note_obj.sudo().search(domain, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_note_history'] = notes.ids[:100]

        values.update({
            'notes': notes.sudo(),
            'page_name': 'custom_note',
            'pager': pager,
            'searchbar_inputs': searchbar_inputs,
            'search': search,
            'search_in': search_in,
            'default_url': '/my/custom_notes_list_view',
        })  
        return request.render("notes_share_portal.custom_portal_my_note_list_view", values)

    @http.route(['/my/custom_open_notes_form_view/<int:note>'], type='http', auth="user", website=True)
    def custom_portal_my_note_form_view(self, note, access_token=None, **kw):
        note_id = request.env['project.task'].sudo().browse(note)

        values = self.custom_note_get_page_view_values(note_id, access_token, **kw)
        return request.render("notes_share_portal.custom_portal_my_note_form_view", values) 