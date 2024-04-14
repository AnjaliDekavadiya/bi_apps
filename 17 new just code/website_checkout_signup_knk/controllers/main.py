# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from werkzeug.exceptions import Forbidden

from odoo import _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.exceptions import UserError


class ElearningWebsiteSale(WebsiteSale):

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = {key: qcontext.get(key) for key in qcontext}
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        remove_keys = ['confirm_password', 'is_create_user', 'submitted', 'callback', 'field_required', 'use_same', 'partner_id']
        try:
            for remove in remove_keys:
                values.pop(remove)
        except:
            pass

        if values.get('email'):
            values.update({'login': values.get('email')})
        if values.get('country_id'):
            values.update({'country_id': int(values.get('country_id'))})
        if values.get('state_id'):
            values.update({'state_id': int(values.get('state_id'))})
        supported_lang_codes = [code for code, _ in request.env['res.lang'].get_installed()]
        lang = request.context.get('lang', '').split('_')[0]
        if lang in supported_lang_codes:
            values['lang'] = lang
        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()

    def _signup_with_values(self, token, values):
        login, password = request.env['res.users'].sudo().signup(values, token)
        request.env.cr.commit()     # as authenticate will use its own cursor we need to commit the current transaction
        uid = request.session.authenticate(request.db, login, password)
        if not uid:
            raise SignupError(_('Authentication Failed.'))

    def _checkout_form_save(self, mode, checkout, all_values):
        partner_id = False
        if all_values.get('mode'):
            all_values.pop('mode')
        if mode[0] == 'new' and mode[1] == 'billing' and all_values.get('is_create_user'):
            self.do_signup(all_values)
            partner_id = request.env.user.partner_id.id
        else:
            Partner = request.env['res.partner']
            if mode[0] == 'new':
                partner_id = Partner.sudo().with_context(tracking_disable=True).create(checkout).id
            elif mode[0] == 'edit':
                partner_id = int(all_values.get('partner_id', 0))
                if partner_id:
                    # double check
                    order = request.website.sale_get_order()
                    shippings = Partner.sudo().search([("id", "child_of", order.partner_id.commercial_partner_id.ids)])
                    if partner_id not in shippings.mapped('id') and partner_id != order.partner_id.id:
                        return Forbidden()
                    Partner.browse(partner_id).sudo().write(checkout)
        return partner_id

    def checkout_form_validate(self, mode, all_form_values, data):
        error, error_message = super(ElearningWebsiteSale, self).checkout_form_validate(mode, all_form_values, data)
        if all_form_values.get('password') != all_form_values.get('confirm_password') and all_form_values.get('is_create_user'):
            error["password"] = 'error'
            error["confirm_password"] = 'error'
            error_message.append(_("Passwords do not match; please retype them."))
        if request.env["res.users"].sudo().search([("login", "=", all_form_values.get('email'))]):
            error["email"] = 'error'
            error_message.append(_("Another user is already registered using this email address."))
        return error, error_message
