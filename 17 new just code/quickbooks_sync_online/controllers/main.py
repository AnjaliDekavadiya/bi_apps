# Copyright 2020 VentorTech OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import http, SUPERUSER_ID, _
from odoo.http import request
from odoo.exceptions import ValidationError

import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

try:
    from werkzeug.exceptions import BadRequest
    from intuitlib.exceptions import AuthClientError
except (ImportError, IOError) as ex:
    _logger.error(ex)


class OAuthController(http.Controller):

    @http.route('/qbo/callback', type='http', auth='user')
    def callback(self, state, code, realmId, *args, **kw):
        """Intuit authentication response handler."""
        response_error = request.params.get('error')
        if response_error:
            return BadRequest(_('Authorizing request error: %s.' % response_error))

        if not (state and code and realmId):
            return BadRequest(_(
                'Invalid Intuit response: %s, %s, %s!' % (state, code, realmId)
            ))

        try:
            company_id = int(state.rsplit('.', maxsplit=1)[-1])
        except Exception as ex:
            _logger.error(ex)
            return BadRequest(_('Bad csrf! Rejected!'))

        company = request.env['res.company']\
            .with_user(SUPERUSER_ID).browse(company_id)

        if state != company.qbo_csrf_token:
            return BadRequest(_('Invalid csrf response! Rejected!'))

        if realmId != company.qbo_company_id:
            return BadRequest(_(
                'Invalid Intuit Company ID! You are trying to connect to the wrong company.'
            ))

        try:
            auth_client = company._qbo_auth_client()
        except ValidationError as ex:
            return BadRequest(ex.args[0])

        try:
            auth_client.get_bearer_token(code, realm_id=realmId)
        except AuthClientError as ex:
            return BadRequest(_(
                'Intuit Access Token error, %s, %s!' % (ex.status_code, ex.content)
            ))

        access_delta = auth_client.expires_in
        refresh_delta = auth_client.x_refresh_token_expires_in
        access_point = datetime.now() + timedelta(seconds=access_delta)
        refresh_point = datetime.now() + timedelta(seconds=refresh_delta)

        company.write({
            'is_authorized': True,
            'is_authenticated': True,
            'qbo_access_token': auth_client.access_token,
            'qbo_refresh_token': auth_client.refresh_token,
            'access_token_update_point': access_point,
            'refresh_token_update_point': refresh_point,
        })
        company._compute_next_call()

        try:
            company._update_intuit_company_info()
        except ValidationError as ex:
            company._revoke_qbo_access()
            return BadRequest(ex.name)

        return request.redirect('/web')
