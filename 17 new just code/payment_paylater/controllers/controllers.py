# -*- coding: utf-8 -*-
import werkzeug

from odoo import http
from odoo.http import request

class PaylaterController(http.Controller):
    _accept_url = '/payment/paylater/feedback'

    @http.route(_accept_url, type='http', auth='public', csrf=False)
    def paylater_form_feedback(self, **post):
        request.env['payment.transaction'].sudo()._handle_notification_data('paylater',post)
        config_setting = request.env['ir.default'].sudo()._get('res.config.settings','transaction_setting') or 'order_place'
        if config_setting == "order_place":
            return werkzeug.utils.redirect('/payment/status')
        else:
            return werkzeug.utils.redirect('/shop/payment/validate')
