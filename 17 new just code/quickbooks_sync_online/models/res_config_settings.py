# Copyright 2020 VentorTech OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    qbo_client_id = fields.Char(
        related='company_id.qbo_client_id',
        readonly=False,
    )
    qbo_client_secret = fields.Char(
        related='company_id.qbo_client_secret',
        readonly=False,
    )
    qbo_redirect_uri = fields.Char(
        related='company_id.qbo_redirect_uri',
    )
    qbo_auth_url = fields.Char(
        related='company_id.qbo_auth_url',
    )
    qbo_csrf_token = fields.Char(
        related='company_id.qbo_csrf_token',
    )
    qbo_access_token = fields.Text(
        related='company_id.qbo_access_token',
    )
    qbo_refresh_token = fields.Char(
        related='company_id.qbo_refresh_token',
    )
    qbo_company_id = fields.Char(
        related='company_id.qbo_company_id',
        readonly=False,
    )
    qbo_company_info = fields.Char(
        related='company_id.qbo_company_info',
    )
    qbo_environment = fields.Selection(
        related='company_id.qbo_environment',
        readonly=False,
    )
    access_token_update_point = fields.Datetime(
        related='company_id.access_token_update_point',
    )
    refresh_token_update_point = fields.Datetime(
        related='company_id.refresh_token_update_point',
    )
    access_token_cron_point = fields.Datetime(
        related='company_id.access_token_cron_point',
    )
    is_authenticated = fields.Boolean(
        related='company_id.is_authenticated',
    )
    is_authorized = fields.Boolean(
        related='company_id.is_authorized',
    )
    qbo_auto_export = fields.Boolean(
        related='company_id.qbo_auto_export',
        readonly=False,
    )
    qbo_payment_sync_in = fields.Boolean(
        related='company_id.qbo_payment_sync_in',
        readonly=False,
    )
    qbo_payment_sync_out = fields.Boolean(
        related='company_id.qbo_payment_sync_out',
        readonly=False,
    )
    qbo_next_call_point = fields.Datetime(
        related='company_id.qbo_next_call_point',
    )
    qbo_export_date_point = fields.Date(
        related='company_id.qbo_export_date_point',
        readonly=False,
    )
    qbo_export_limit = fields.Integer(
        related='company_id.qbo_export_limit',
        readonly=False,
    )
    qbo_default_stock_valuation_account_id = fields.Many2one(
        related='company_id.qbo_default_stock_valuation_account_id',
        readonly=False,
    )
    qbo_default_write_off_account_id = fields.Many2one(
        related='company_id.qbo_default_write_off_account_id',
        readonly=False,
    )
    qbo_sync_product = fields.Boolean(
        related='company_id.qbo_sync_product',
        readonly=False,
    )
    qbo_sync_product_category = fields.Boolean(
        related='company_id.qbo_sync_product_category',
        readonly=False,
    )
    qbo_sync_storable_to_consumable = fields.Boolean(
        related='company_id.qbo_sync_storable_to_consumable',
        readonly=False,
    )
    qbo_export_out_invoice = fields.Boolean(
        related='company_id.qbo_export_out_invoice',
        readonly=False,
    )
    qbo_export_out_refund = fields.Boolean(
        related='company_id.qbo_export_out_refund',
        readonly=False,
    )
    qbo_export_in_invoice = fields.Boolean(
        related='company_id.qbo_export_in_invoice',
        readonly=False,
    )
    qbo_export_in_refund = fields.Boolean(
        related='company_id.qbo_export_in_refund',
        readonly=False,
    )
    qbo_def_journal_id = fields.Many2one(
        related='company_id.qbo_def_journal_id',
        readonly=False,
    )
    qbo_cus_pay_point = fields.Char(
        related='company_id.qbo_cus_pay_point',
        readonly=False,
    )
    qbo_ven_pay_point = fields.Char(
        related='company_id.qbo_ven_pay_point',
        readonly=False,
    )

    def get_qbo_credentials(self):
        """Application authorization via previously generated URL."""
        company = self.company_id
        if not company:
            return False

        company.clear_caches()
        company._generate_qbo_auth_url()

        return {
            'type': 'ir.actions.act_url',
            'url': self.qbo_auth_url,
            'target': 'new',
        }

    def refresh_qbo_access_token_settings(self):
        """
        Before an application can access data using QuickBooks Online API, it must
        obtain an access token that grants access to the API. Validity for Intuit’s
        access_token is 60 min. A fresh access_token can be retrieved by calling
        the current method.
        """
        result = list()
        for company in self.mapped('company_id'):
            x = company._refresh_qbo_access_token()
            y = company._update_intuit_company_info()
            result.append((x, y))
        return result

    def revoke_qbo_access_settings(self):
        """Revoke access to the Intuit company."""
        return [x._revoke_qbo_access() for x in self.mapped('company_id')]
