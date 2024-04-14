# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from odoo import fields, http
from odoo.http import request
from odoo.tools.translate import _
import math, random
import uuid
from odoo.exceptions import UserError
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.home import ensure_db, Home, SIGN_UP_REQUEST_PARAMS, LOGIN_SUCCESSFUL_PARAMS
from odoo.addons.auth_signup.controllers.main import AuthSignupHome


class OtpHome(http.Controller):
    def GenerateOtp(self):
        digits = "0123456789"
        OTP = ""
        for i in range(6) :
            OTP += digits[math.floor(random.random() * 10)]

        return OTP

    @http.route('/check/login', type='json', auth='public', website=True)
    def check_login(self, login):
        users = request.env['res.users'].sudo().search([('login', '=', login)])
        if not users:
            users = request.env['res.users'].sudo().search([('email', '=', login)])
        if len(users) != 1:
            return True


    @http.route('/send/otp', type='json', auth='public', website=True)
    def send_otp(self, login, name):
        Otp_obj = request.env['otp.otp']
        OTP = self.GenerateOtp()
        if OTP:
            obj = Otp_obj.sudo().create({
                'otp_name': OTP,
                'name':OTP,
                'user_email': login,
            })
            obj.send_otp_mail(OTP, login, name)
            otp_id = obj.id
            return otp_id

    @http.route('/verify/otp', type='json', auth='public', website=True)
    def verify_otp(self, Otpid):
        Otp_obj = request.env['otp.otp'].sudo().browse(Otpid)
        Otp_obj.unlink()

class WebHome(Home):

    @http.route()
    def web_login(self, redirect=None, **kw):
        ensure_db()
        response = super(WebHome, self).web_login(**kw)
        if 'otp_type' in request.params:
            otp_obj = request.env['otp.otp'].sudo().search([('is_used','=',False),('user_email','=',request.params['login'])], limit=1, order="id desc")
            if otp_obj and 'password' in request.params and otp_obj.name == request.params['password']:
                user = request.env['res.users'].sudo().search([('login','=',request.params['login'])])
                if user.has_group('base.group_user'):
                    url = '/web'
                else:
                    url = '/my'

                uid = request.session.authenticate(request.db, request.params['login'], otp_obj.otp_name)
                request.params['login_success'] = True
                
                otp_obj.update({'is_used':True})
                other_otp = request.env['otp.otp'].sudo().search([('name','!=',otp_obj.name),('user_email','=',request.params['login']),('is_used','=',False)])
                for otp in other_otp:
                    otp.is_used = True
                # return resp
                return request.redirect(self._login_redirect(uid, redirect=redirect))
            else:
                response.qcontext['error'] = _("Please enter valid OTP.")
        return response


class SignupHome(AuthSignupHome):
   
    def do_signup(self, qcontext):
        if 'otp' in request.params:
            otp_obj = request.env['otp.otp'].sudo().search([('is_used','=',False),('user_email','=',request.params['login'])], limit=1, order="id desc")
            if otp_obj and otp_obj.name == request.params['otp']:
                otp_obj.update({'is_used':True})
                other_otp = request.env['otp.otp'].sudo().search([('name','!=',otp_obj.name),('user_email','=',request.params['login']),('is_used','=',False)])
                for otp in other_otp:
                    otp.is_used = True
            else:
                raise UserError(_("Please enter valid OTP."))
        return super().do_signup(qcontext)