# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. 
# See LICENSE file for full copyright and licensing details.

import base64
from collections import OrderedDict

from odoo import http, _
from odoo.http import request
from odoo.tools import image_process
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager


class CustomerPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'purchase_agreement_count' in counters:
            partner = request.env.user.partner_id
            purchase_ids = request.env['purchase.order'].sudo().search([('partner_id', '=', partner.id)])
            purchase_agreement_ids = request.env['purchase.requisition'].sudo().search([
                '|', ('vendor_id', 'child_of', [partner.commercial_partner_id.id]),
                ('purchase_ids', 'in', purchase_ids.ids)
            ])
            values['purchase_agreement_count'] = len(purchase_agreement_ids.ids)
        return values

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        purchase_ids = request.env['purchase.order'].sudo().search([('partner_id', '=', partner.id)])
        purchase_agreement_ids = request.env['purchase.requisition'].sudo().search([
            '|', ('vendor_id', 'child_of', [partner.commercial_partner_id.id]),
            ('purchase_ids', 'in', purchase_ids.ids)
        ])
        values.update({
            'purchase_agreement_count': len(purchase_agreement_ids),
        })
        return values

    @http.route(['/my/purchase/cust_agreements', '/my/purchase/cust_agreements/page/<int:page>'], type='http', auth="user", website=True)
    def custom_portal_my_purchase_agreements(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        PurchaseAgreement = request.env['purchase.requisition'].sudo()

        purchase_ids = request.env['purchase.order'].sudo().search([('partner_id', '=', partner.id)])

        domain = [
            '|', ('vendor_id', 'child_of', [partner.commercial_partner_id.id]),
            ('purchase_ids', 'in', purchase_ids.ids)
        ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'ordering_date desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }

        # default sortby order
        if not sortby or sortby not in searchbar_sortings:
            sortby = 'name'
        sort_order = searchbar_sortings[sortby]['order']


        # count for pager
        purchase_agreement_count = PurchaseAgreement.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/purchase/cust_agreements",
            url_args={'sortby': sortby},
            total=purchase_agreement_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        purchase_agreements = PurchaseAgreement.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_purchase_agreements_history'] = purchase_agreements.ids[:100]

        values.update({
            'date': date_begin,
            'purchase_agreements': purchase_agreements.sudo(),
            'page_name': 'purchase_agreement',
            'pager': pager,
            'default_url': '/my/purchase/cust_agreements',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("vendor_tendor_portal_website.portal_vendor_cust_purchase_agreements", values)
    
    @http.route(['/my/purchase/cust_agreements/<int:purchase_agreement_id>'], type='http', auth="public", website=True)
    def custom_portal_my_purchase_agreement(self, purchase_agreement_id, **kw):
        purchase_agreement = request.env['purchase.requisition'].sudo().browse(purchase_agreement_id)
        partner = request.env.user.partner_id

        purchase_ids = request.env['purchase.order'].sudo().search([('partner_id', '=', partner.id)])

        values = {
            'page_name': 'purchase_agreement',
            'purchase_agreement': purchase_agreement,
            'purchase_ids': purchase_ids
        }
        history = request.session.get('my_purchase_agreements_history', [])
        values.update(get_records_pager(history, purchase_agreement))
        return request.render('vendor_tendor_portal_website.vendor_purchase_cust_agreement_portal_template', values)

    @http.route(['/my/cust_agreements/purchase', '/my/cust_agreements/purchase/page/<int:page>'], type='http', auth="user", website=True)
    def custom_portal_my_agreements_purchase_orders(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        PurchaseOrder = request.env['purchase.order']

        purchase_agreement = request.env['purchase.requisition'].sudo().browse(int(kw.get('purchase_agreement')))
        domain = [('id', 'in', purchase_agreement.purchase_ids.ids)]

        # archive_groups = self._get_archive_groups('purchase.order', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc, id desc'},
            'name': {'label': _('Name'), 'order': 'name asc, id asc'},
            'amount_total': {'label': _('Total'), 'order': 'amount_total desc, id desc'},
        }
        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'purchase': {'label': _('Purchase Order'), 'domain': [('state', '=', 'purchase')]},
            'cancel': {'label': _('Cancelled'), 'domain': [('state', '=', 'cancel')]},
            'done': {'label': _('Locked'), 'domain': [('state', '=', 'done')]},
            'rfqs': {'label': _('RFQs'), 'domain': [('state', '=', 'draft')]},
        }
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # count for pager
        purchase_count = PurchaseOrder.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/cust_agreements/purchase",
            url_args={'date_begin': date_begin, 'date_end': date_end},
            total=purchase_count,
            page=page,
            step=self._items_per_page
        )
        # search the purchase orders to display, according to the pager data
        orders = PurchaseOrder.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        request.session['my_purchases_history'] = orders.ids[:100]

        values.update({
            'date': date_begin,
            'agreement_orders': orders,
            'purchase_agreement': purchase_agreement,
            'page_name': 'agreement_purchases',
            'pager': pager,
            # 'archive_groups': archive_groups,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'default_url': '/my/cust_agreements/purchase',
        })
        return request.render("vendor_tendor_portal_website.portal_cust_agreement_purchase_orders", values)

    @http.route(['/my/cust_agreement/purchase/<int:order_id>'], type='http', auth="public", website=True)
    def custom_portal_my_agreement_purchase_order(self, order_id=None, access_token=None, **kw):
        # def resize_to_48(b64source):
        #     if not b64source:
        #         b64source = base64.b64encode(Binary().placeholder())
        #     return image_process(b64source, size=(48, 48))
        def resize_to_48(source):
            if not source:
                source = request.env['ir.binary']._placeholder()
            else:
                source = base64.b64decode(source)
            return base64.b64encode(image_process(source, size=(48, 48)))
        try:
            order_sudo = self._document_check_access('purchase.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = {
            'order': order_sudo,
            'purchase_agreement': order_sudo.requisition_id,
            'page_name': 'agreement_purchase',
            'resize_to_48': resize_to_48,
        }
        return request.render("vendor_tendor_portal_website.portal_cust_agreement_purchase_order", values)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
