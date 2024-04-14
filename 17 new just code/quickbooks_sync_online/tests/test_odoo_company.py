# Copyright 2020 VentorTech OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from .config.intuit_case import request_client
from .config.intuit_case import IntuitCred, OdooCompanyInit

from odoo.tests import tagged
from odoo.tools import mute_logger
from odoo.exceptions import ValidationError

import logging
from unittest.mock import patch

_logger = logging.getLogger(__name__)

try:
    from quickbooks import QuickBooks
    from intuitlib.client import AuthClient
except (ImportError, IOError) as ex:
    _logger.error(ex)


@tagged('-at_install', '-standard', 'post_install', 'qbo_test_company')
class TestOdooCompanySettings(OdooCompanyInit):

    def setUp(self):
        super(TestOdooCompanySettings, self).setUp()

    def test_company_get_qbo_env(self):
        env = self.company.get_qbo_env()
        self.assertEqual(env, 'sandbox')

    def test_company_redirect_uri(self):
        su = self.env['ir.config_parameter'].sudo()
        redirect_uri_ = su.get_param('web.base.url') + '/qbo/callback'
        self.assertEqual(self.company.qbo_redirect_uri, redirect_uri_)

    def test_cron_nex_call(self):
        self.company._compute_next_call()
        cron = self.env.ref(
            'quickbooks_sync_online.trigger_invoice_to_qbo_cron',
            raise_if_not_found=False,
        )
        if cron:
            self.assertEqual(self.company.qbo_next_call_point, cron.nextcall)

    def test_access_token_cron_point(self):
        self.company._compute_access_token_cron_point()
        cron = self.env.ref(
            'quickbooks_sync_online.refresh_qbo_access_token_cron',
            raise_if_not_found=False,
        )
        if cron:
            self.assertEqual(self.company.access_token_cron_point, cron.nextcall)

    def test_company_auth_client(self):
        # No raise
        client = self.company._qbo_auth_client()
        self.assertIsInstance(client, AuthClient)

        # Raise if not 'qbo_client_secret'
        self.company.write({'qbo_client_secret': False})
        with self.assertRaises(ValidationError):
            self.company._qbo_auth_client()

        # Raise if not 'qbo_client_id'
        self.company.write({
            'qbo_client_id': False,
            'qbo_client_secret': IntuitCred.client_secret,
        })
        with self.assertRaises(ValidationError):
            self.company._qbo_auth_client()
        self.company.write({'qbo_client_id': IntuitCred.client_id})

    @patch(request_client)
    def test_get_request_client(self, *args):
        with self.assertRaises(ValidationError):
            self.company.get_request_client()

        self.company.write({
            'qbo_refresh_token': IntuitCred.qbo_refresh_token,
        })
        qbo_object = self.company.get_request_client()
        self.assertIsInstance(qbo_object, QuickBooks)

    def test_settings_get_qbo_credentials(self):
        self.company.write({'qbo_auth_url': False})
        act_url = self.settings.get_qbo_credentials()

        self.assertIsInstance(act_url, dict)
        self.assertEqual(act_url.get('type'), 'ir.actions.act_url')
        self.assertEqual(act_url.get('url'), self.company.qbo_auth_url)
        self.assertEqual(act_url.get('target'), 'new')

    @mute_logger('odoo.addons.quickbooks_sync_online.models.res_company')
    def test_check_company_status(self):
        with self.assertRaises(ValidationError):
            self.company._check_qbo_auth()

        self.company.write({
            'is_authenticated': True,
        })
        with self.assertRaises(ValidationError):
            self.company._check_qbo_auth()

        self.company.write({
            'is_authorized': True,
            'is_authenticated': False,
        })
        with self.assertRaises(ValidationError):
            self.company._check_qbo_auth()

        self.company.write({
            'is_authenticated': True,
        })
        self.company._check_qbo_auth()

    def test_intuit_company_info(self):
        self._set_up_connection()
        self.assertTrue(self.company.intuit_is_us_company())

    def test_prepare_email_subscribers(self):
        prepared_user_ids = self.company._prepare_subscribers()
        self.assertIn(self.user.partner_id.id, prepared_user_ids)
