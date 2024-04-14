# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.osv.expression import OR
from collections import OrderedDict

# from odoo.addons.website_portal.controllers.main import website_account
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

class CustomerPortal(CustomerPortal):
    
    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        PosOrder = request.env['pos.order'].search([])
        pos_count = PosOrder.search_count([
            ('partner_id', 'child_of', [partner.commercial_partner_id.id])
        ])
        values.update({
            'pos_count': pos_count,
        })
        return values
    
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        PosOrder = request.env['pos.order'].search([])
        pos_count = PosOrder.search_count([
            ('partner_id', 'child_of', [partner.commercial_partner_id.id])
        ])
        values.update({
            'pos_count': pos_count,
        })
        return values

    # POS Orders
    @http.route(['/my/pos_orders', '/my/pos_orders/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_pos_orders(self, page=1, date_begin=None, date_end=None, sortby=None,search=None,filterby=None, search_in='content', **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        pos_order = request.env['pos.order']
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'date_order desc'},
            'name': {'label': _('Name'), 'order': 'name asc'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters[filterby]['domain']
        domain = [
            ('partner_id', 'child_of', [partner.commercial_partner_id.id])
        ]
        # pager
        pager = portal_pager(
            url="/my/pos_orders",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby, 'search_in': search_in, 'search': search},
            total=values.get('pos_count'),
            page=page,
            step=self._items_per_page
        )
        searchbar_inputs = {
            'customer': {'input': 'customer', 'label': _('Search in Salesperson')},
            'all': {'input': 'all', 'label': _('Search in Order No')},
        }

        if search and search_in:
            search_domain = []
            if search_in in ('content', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            if search_in in ('customer', 'all'):
                search_domain = OR([search_domain, [('user_id.name', 'ilike', search)]])
            domain += search_domain

        pos_count = request.env['pos.order'].search_count(domain)

        # content according to pager and archive selected
        orders = pos_order.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        values.update({
            'pos_orders': orders,
            'page_name': 'pos_order',
            'pager': pager,
            'default_url': '/my/pos_orders',
            'searchbar_sortings':searchbar_sortings,
            'sortby': sortby,
            'search_in': search_in,
            'searchbar_inputs': searchbar_inputs,
            'filterby': filterby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
        })
        return request.render("website_portal_pos_orders.portal_my_pos_orders", values)
    
    @http.route(['/pos_orders/printpos/<int:order_id>'], type='http', auth="public", website=True)
    def portal_pos_order_report(self, order_id, access_token=None, **kw):
        try:
            order_sudo = self._document_check_access('pos.order',order_id, access_token) #method name changed to _document_check_access in odoo12
        except AccessError:
            print("WEXRTCVYGBHNJ")
            return request.redirect('/my')

        # print report as sudo, since it require access to taxes, payment term, ... and portal
        # does not have those access rights.
#         pdf = request.env.ref('pos_order_report.pos_order_id').sudo().render_qweb_pdf([order_id])[0]
        # pdf = request.env.ref('website_portal_pos_orders.portal_pos_order_id').sudo()._render_qweb_pdf([order_id])[0] #odoo13
        pdf, _ = request.env['ir.actions.report'].sudo()._render_qweb_pdf('website_portal_pos_orders.portal_pos_order_id', [order_id])
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)



