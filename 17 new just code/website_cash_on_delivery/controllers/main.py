# -*- coding: utf-8 -*-

import pprint
import logging
from odoo.http import request
from odoo import http, tools, _
from odoo.addons.website_sale.controllers.main import WebsiteSale
_logger = logging.getLogger(__name__)

class WebsiteSale(WebsiteSale):
    @http.route(['/shop/cod/status'], type='json', auth='user')
    def _check_product_cod_status(self, product_id):
        product = request.env['product.product'].browse(int(product_id))
        if not request.env.user.partner_id.is_cod_applicable:
            return {'status': False, 'class': 'alert-danger', 'message': 'Customer Not Available For Cash On Delivery!'}
        elif not product.not_allow_cod:
            return {'status': False, 'class': 'alert-success', 'message': 'Cash On Delivery Available!'}
        elif product.not_allow_cod:
            return {'status': False, 'class': 'alert-danger', 'message': 'Cash On Delivery Not Available!'}
        else:
            return {'status': True}

class CodController(http.Controller):
    _accept_url = '/payment/cod/feedback'

    @http.route([
        '/payment/cod/feedback',
    ], type='http', auth='none', csrf=False)
    def cod_form_feedback(self, **post):
#        _logger.info('Beginning form_feedback with post data %s', pprint.pformat(post))  # debug
#        request.env['payment.transaction'].sudo().form_feedback(post, 'cod')
#        return werkzeug.utils.redirect('/payment/process')
        
        order = request.env['sale.order'].sudo().browse(request.session.get('sale_last_order_id'))
        _logger.info('Beginning form_feedback with post data %s', pprint.pformat(post))  # debug
        post.update({"sale_order_id": order.id})
        tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
            'cod', post
        )#16
        tx_sudo._handle_notification_data('cod', post)#16
        return request.redirect('/payment/status')

#class WebsiteSale(WebsiteSale):

    # Fully override
#    def _get_shop_payment_values(self, order, **kwargs):
#        if order.is_cod:
#            return super(WebsiteSale, self)._get_shop_payment_values(order, **kwargs)
#        if not order.is_cod:
#            kwargs.get('kwargs').update({
#                'custom_sale_order_cod': order
#            })
#        return super(WebsiteSale, self)._get_shop_payment_values(order=order, kwargs=kwargs)
#        values = dict(
#            website_sale_order=order,
#            errors=[],
#            partner=order.partner_id.id,
#            order=order,
#            payment_action_id=request.env.ref('payment.action_payment_acquirer').id,
#            return_url= '/shop/payment/validate',
#            bootstrap_formatting= True
#        )

#        domain = expression.AND([
#            ['&', ('state', 'in', ['enabled', 'test']), ('company_id', '=', order.company_id.id)],
#            ['|', ('website_id', '=', False), ('website_id', '=', request.website.id)],
#            ['|', ('country_ids', '=', False), ('country_ids', 'in', [order.partner_id.country_id.id])]
#        ])
#        if not order.is_cod: #custom
#            domain.extend([('provider', '!=', 'cod')]) #custom

#        acquirers = request.env['payment.acquirer'].search(domain)

#        values['access_token'] = order.access_token
#        values['acquirers'] = [acq for acq in acquirers if (acq.payment_flow == 'form' and acq.view_template_id) or
#                                    (acq.payment_flow == 's2s' and acq.registration_view_template_id)]
#        values['tokens'] = request.env['payment.token'].search(
#            [('partner_id', '=', order.partner_id.id),
#            ('acquirer_id', 'in', acquirers.ids)])

#        if order:
#            values['acq_extra_fees'] = acquirers.get_acquirer_extra_fees(order.amount_total, order.currency_id, order.partner_id.country_id.id)
#        return values

#     def _get_shop_payment_values(self, order, **kwargs):
#         if order.is_cod:
#             return super(WebsiteSale, self)._get_shop_payment_values(order, **kwargs)
# 
#         shipping_partner_id = False
#         if order:
#             shipping_partner_id = order.partner_shipping_id.id or order.partner_invoice_id.id
# 
#         values = dict(
#             website_sale_order=order,
#             errors=[],
#             partner=order.partner_id.id,
#             order=order,
#             payment_action_id=request.env.ref('payment.action_payment_acquirer').id,
#             return_url= '/shop/payment/validate',
#             bootstrap_formatting= True
#         )
# 
#         if order.is_cod:
#            acquirers = request.env['payment.acquirer'].search(
#                [('website_published', '=', True),
#                 ('company_id', '=', order.company_id.id)]
#            )
#         else:
#             acquirers = request.env['payment.acquirer'].search(
#                 [('website_published', '=', True),
#                  ('company_id', '=', order.company_id.id),
#                  ('provider', '!=', 'cod')]
#             )
# 
#         values['form_acquirers'] = [acq for acq in acquirers if acq.payment_flow == 'form' and acq.view_template_id]
#         values['s2s_acquirers'] = [acq for acq in acquirers if acq.payment_flow == 's2s' and acq.registration_view_template_id]
#         values['tokens'] = request.env['payment.token'].search(
#             [('partner_id', '=', order.partner_id.id),
#             ('acquirer_id', 'in', [acq.id for acq in values['s2s_acquirers']])])
# 
#         for acq in values['form_acquirers']:
#             acq.form = acq.with_context(
#                     submit_class='btn btn-primary',
#                     submit_txt=_('Pay Now')
#                 ).sudo().render(
#                 '/',
#                 order.amount_total,
#                 order.pricelist_id.currency_id.id,
#                 values={
#                     'return_url': '/shop/payment/validate',
#                     'partner_id': shipping_partner_id,
#                     'billing_partner_id': order.partner_invoice_id.id,
#                 }
#             )
#         return values

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
