# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.exceptions import AccessError, MissingError

from odoo.http import request

from collections import OrderedDict
from odoo.osv.expression import OR

# from odoo.addons.website_portal.controllers.main import website_account
from odoo.addons.portal.controllers.portal import CustomerPortal as website_account

class website_account(website_account):
    
    def _prepare_portal_layout_values(self): # odoo11
        values = super(website_account, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        payment = request.env['account.payment']
        payment_count = payment.sudo().search_count([
          ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
          ('payment_type', 'in', ['inbound', 'outbound']),
          ('state','in',['posted','sent','reconciled'])
          ])
        values.update({
            'custom_payment_count': payment_count,
        })
        return values

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        payment = request.env['account.payment']
        payment_count = payment.sudo().search_count([
          ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
          ('payment_type', 'in', ['inbound', 'outbound']),
          ('state','in',['posted','sent','reconciled'])
          ])
        values.update({
            'custom_payment_count': payment_count,
        })
        return values

    
    
#     @http.route()
#     def account(self, **kw):
#         """ Add payment documents to main account page """
#         response = super(website_account, self).account(**kw)
#         partner = request.env.user.partner_id
#         payment = request.env['account.payment']
#         payment_count = payment.sudo().search_count([
#           ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
#             ('payment_type', 'in', ['inbound', 'outbound']),
#           ('state','in',['posted','sent','reconciled'])
#           ])
#         response.qcontext.update({
#             'payment_count': payment_count,
#         })
#         return response
    
    # Payments
    @http.route(['/my/custom_payments', '/my/custom_payments/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_payments(self, page=1, sortby=None, filterby=None, search=None, search_in='content', groupby='none', **kw):
        values = self._prepare_portal_layout_values()
        
        partner = request.env.user.partner_id
        AccountPayment = request.env['account.payment']
        domain = [
            ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
            ('payment_type', 'in', ['inbound', 'outbound']),
            ('state','in',['posted','sent','reconciled'])
        ]
        
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'journal': {'label': _('Journal'), 'order': 'journal_id desc'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'Vendor Payments': {'label': _('Vendor Payments'), 'domain': [('payment_type','=','outbound')]},
            'Customer Payments': {'label': _('Customer Payments'), 'domain': [('payment_type','=','inbound')]},
            'Transfers': {'label': _('Transfers'), 'domain': [('payment_type','=','transfer')]},
            'Draft': {'label': _('Draft'), 'domain': [('state','=','draft')]},
            'Posted': {'label': _('Posted'), 'domain': [('state','=','posted')]},
            'Sent': {'label': _('Sent'), 'domain': [('state','=','sent')]},
            'Reconciled': {'label': _('Reconciled'), 'domain': [('state','=','reconciled')]},
        }
        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Search <span class="nolabel"> (in Ref. Number #)</span>')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'journal': {'input': 'journal', 'label': _('Journal')},
            'payment_method': {'input': 'payment_method', 'label': _('Payment Method')},
            'state': {'input': 'state', 'label': _('State')},
        }
        
        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']
        
        # search
        if search and search_in:
            search_domain = []
            if search_in in ('content', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            domain += search_domain

        # default group by value
        if groupby == 'journal':
            order = "journal_id, %s" % order
        if groupby == 'payment_method':
            order = "payment_method_id, %s" % order
        if groupby == 'state':
            order = "state, %s" % order

        # count for pager
        payment_count = AccountPayment.sudo().search_count(domain)
        # pager
        pager = request.website.pager(
            url="/my/custom_payments",
            total=payment_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        payments = AccountPayment.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        values.update({
            'payments': payments,
            'page_name': 'payment',
            'pager': pager,
            'default_url': '/my/custom_payments',
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'sortby': sortby,
            'groupby': groupby,
        })
        return request.render("website_portal_payments.portal_my_payments", values)
    
#     @http.route(['/custom_payment/printpayment/<model("account.payment"):payment>'], type='http', auth="user", website=True)
#     def print_payment(self, payment):
#         if payment:
# #             pdf = request.env['report'].sudo().get_pdf([payment.id], 'website_portal_payments.print_payment_report_web', data=None)
#             report_action = 'account.action_report_payment_receipt'
#             pdf = request.env.ref(report_action).sudo()._render_qweb_pdf([payment.id])[0]
#             pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
#             return request.make_response(pdf, headers=pdfhttpheaders)
#         else:
#             return request.redirect('/payment')

    @http.route(['/custom_payment/printpayment/<model("account.payment"):payment>'], type='http', auth="user", website=True)
    def print_payment(self, payment, access_token=None, report_type='pdf', download=False, **kw):
        try:
            payment_sudo = self._document_check_access('account.payment', payment.id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=payment_sudo, report_type=report_type, report_ref='account.action_report_payment_receipt', download=download)

        return request.redirect('/my')