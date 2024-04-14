# -*- coding: utf-8 -*-

from odoo import http, tools, _
from odoo import api, fields, models, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
import logging
import pprint
import werkzeug

_logger = logging.getLogger(__name__)


class WalletController(http.Controller):
#    _accept_url = '/payment/wallet/feedback'
    _return_url = '/payment/wallet/return'

#    @http.route([
#        '/payment/wallet/feedback',
#    ], type='http', auth='none', csrf=False)
#    def wallet_form_feedback(self, **post):

    @http.route(_return_url, type='http', auth='public', methods=['POST'], csrf=False)
    def wallet_return_from_redirect(self, **data):
        order = request.env['sale.order'].sudo().browse(request.session.get('sale_last_order_id'))
#         if order.payment_tx_id.acquirer_id.provider == 'wallet':
#        if order.transaction_ids and order.transaction_ids[0].acquirer_id.provider == 'wallet':
        if order.transaction_ids and order.transaction_ids[0].provider_id.code == 'wallet':
            if order.partner_id.wallet_balance < float(data.get('wallet_amount')):
                return werkzeug.utils.redirect('/low/blance')
        _logger.info('Beginning form_feedback with post data %s', pprint.pformat(data))  # debug
        data.update({"sale_order_id": order.id})
#        request.env['payment.transaction'].sudo().form_feedback(post, 'wallet')
#        return werkzeug.utils.redirect(post.pop('return_url', '/'))
#        request.env['payment.transaction'].sudo()._handle_feedback_data('wallet', data)
        tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
            'wallet', data
        )#16
        tx_sudo._handle_notification_data('wallet', data)#16
        return request.redirect('/payment/status')

class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'wallets_count' in counters:
            wallet = request.env['customer.wallet']
            wallets_count = wallet.sudo().search_count([
                ('customer_id', '=', request.env.user.partner_id.id)
            ])
            values.update({
                'wallets_count': wallets_count,
            })
        return values

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        wallet = request.env['customer.wallet']
        wallets_count = wallet.sudo().search_count([
            ('customer_id', '=', request.env.user.partner_id.id)
        ])
        values.update({
            'wallets_count': wallets_count,
        })
        return values
    
    @http.route(['/my/wallets', '/my/wallets/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_wallet(self, page=1,date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='content', **kw):
        values = self._prepare_portal_layout_values()
        wallet = request.env['customer.wallet']
        domain = [
            ('customer_id', '=', request.env.user.partner_id.id)
        ]
        # count for pager
        wallets_count = wallet.sudo().search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/wallets",
            total=wallets_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        wallet_list = wallet.sudo().search(domain, limit=self._items_per_page, offset=pager['offset'],order="name desc")
        category_id = request.env.ref('customer_website_wallet.product_wallet_public_category')
        values.update({
            'wallets': wallet_list,
            'page_name': 'wallets',
            'pager': pager,
            'category_id': category_id,
            'default_url': '/my/wallets',
        })
        return request.render("customer_website_wallet.display_wallets", values)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
