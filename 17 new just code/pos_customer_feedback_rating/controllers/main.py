# -*- coding: utf-8 -*-

import base64
from odoo import fields, http, _
from odoo.http import request

class WebsitePOSFeedback(http.Controller):
    @http.route(['/custom_pos_email/feedback/<int:order_id>-<int:user_id>-<int:partner_id>'], type='http', auth='public', website=True)
    def custom_pos_mail_feedback(self, order_id, user_id, partner_id, **kw):
        values = {}
        pos_order_id = request.env['pos.order'].sudo().browse(order_id)
        if user_id == pos_order_id.user_id.id and partner_id == pos_order_id.partner_id.id:
            values.update({
                'pos_order_id': pos_order_id,
                'request_id':order_id,
            })
            return request.render("pos_customer_feedback_rating.custom_pos_customer_feedback_temp", values)

    @http.route(['/custom_pos_customer/feedback/'], type='http', auth='public', website=True)
    def custom_start_rating(self, access_token=None, **kw):
        request_id = kw['request_id']
        order_id = request.env['pos.order'].sudo().browse(int(request_id))
        vals = {
              'custom_service_rating':kw['star'],
              'custom_product_rating':kw['product'],
              'custom_price_rating':kw['price'],
              'custom_Waitting_rating':kw['waitting'],
              'custom_shopping_experiences_rating':kw['experiences'],
              'custom_comment':kw['comment'],
            }
        order_id.sudo().write(vals)
        customer_msg = _(order_id.sudo().partner_id.name + 'has send this feedback rating is %s and comment is %s') % (kw['star'],kw['comment'],)
        return request.render('pos_customer_feedback_rating.custom_pos_feedback_rating_successful_probc',{'order_id':order_id})

    @http.route(['/custom_pos_email/unsubscribe/<int:order_id>'], type='http', auth='public', website=True)
    def custom_POS_email_unsubscribe(self, order_id, **kw):
        values = {}
        pos_order_id = request.env['pos.order'].sudo().browse(order_id)
        if pos_order_id.partner_id.custom_send_feedback_mail:
            pos_order_id.sudo().partner_id.custom_send_feedback_mail = False
        return request.render('pos_customer_feedback_rating.custom_pos_unsubscribe_successful_probc')