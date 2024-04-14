# Copyright 2020 VentorTech OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from .utils import QboCompanyInfo, COMPANY_FIELDS_TO_RESET
from .qbo_transaction_mixin import MODELS_TO_EXPORT

from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import ormcache

import logging
from functools import reduce
from datetime import date, datetime, timedelta

_logger = logging.getLogger(__name__)

try:
    import requests
    from quickbooks import QuickBooks
    from quickbooks.objects.preferences import Preferences
    from quickbooks.objects.company_info import CompanyInfo
    from quickbooks.objects.companycurrency import CompanyCurrency
    from intuitlib.enums import Scopes
    from intuitlib.client import AuthClient
    from intuitlib.utils import generate_token
    from intuitlib.utils import get_auth_header
    from intuitlib.exceptions import AuthClientError
    from future.moves.urllib.parse import urlencode
except (ImportError, IOError) as ex:
    _logger.error(ex)


MINOR_VERSION = 63  # Version of the Intuit API.

MODELS_TO_UPDATE = [
    'res.partner',
]
QBO_FIELDS_TO_ERASE = {
    'qbo_environment': 'production',
    'qbo_company_info': False,
    'qbo_company_country_iso': False,
    'qbo_csrf_token': False,
    'qbo_access_token': False,
    'qbo_refresh_token': False,
    'qbo_auth_url': False,
    'access_token_update_point': False,
    'refresh_token_update_point': False,
    'qbo_export_date_point': date.today(),
    'is_authenticated': False,
    'is_authorized': False,
    'qbo_auto_export': False,
    'qbo_sync_product': True,
    'qbo_sync_product_category': False,
    'qbo_export_out_invoice': True,
    'qbo_export_out_refund': True,
    'qbo_export_in_invoice': True,
    'qbo_export_in_refund': True,
}
ACCESS_TOKEN_URL = 'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer'


class Company(models.Model):
    _inherit = 'res.company'

    qbo_client_id = fields.Char(
        string='Client ID',
    )
    qbo_client_secret = fields.Char(
        string='Client Secret',
    )
    qbo_redirect_uri = fields.Char(
        string='Redirect URI',
        compute='_compute_redirect_uri',
        readonly=True,
    )
    qbo_auth_url = fields.Char(
        string='Auth URL',
    )
    qbo_access_token = fields.Text(
        string='Access Token',
    )
    qbo_refresh_token = fields.Char(
        string='Refresh Token',
    )
    qbo_company_id = fields.Char(
        string='Company ID',
    )
    qbo_company_info = fields.Char(
        string='Company Info',
        readonly=True,
    )
    qbo_company_country_iso = fields.Char(
        string='Company Country Iso',
    )
    qbo_csrf_token = fields.Char(
        string='Expected CSRF',
        readonly=True,
    )
    qbo_environment = fields.Selection(
        selection=[
            ('production', 'Production'),
            ('sandbox', 'Developing'),
        ],
        string='Environment',
        default='production',
    )
    access_token_update_point = fields.Datetime(
        string='Validation access token',
    )
    refresh_token_update_point = fields.Datetime(
        string='Updating refresh token',
    )
    access_token_cron_point = fields.Datetime(
        string='Auto updating access token',
        compute='_compute_access_token_cron_point',
    )
    is_authenticated = fields.Boolean(
        string='Is authenticated',
        readonly=True,
    )
    is_authorized = fields.Boolean(
        string='Is authorized',
        readonly=True,
    )
    qbo_auto_export = fields.Boolean(
        string='Automatic Invoice/Bills Export to QBO',
    )
    qbo_payment_sync_in = fields.Boolean(
        string='Automatic Payment Import to Odoo',
    )
    qbo_payment_sync_out = fields.Boolean(
        string='Automatic Payment Export to QBO',
    )
    qbo_cus_pay_point = fields.Char(
        string='Last Customer Payment Point',
        size=30,
        help='The last fetched customer datetime payment point from Quickbooks.',
    )
    qbo_ven_pay_point = fields.Char(
        string='Last Vendor Payment Point',
        size=30,
        help='The last fetched vendor datetime payment point from Quickbooks.',
    )
    qbo_export_date_point = fields.Date(
        string='Export Date Point',
        required=True,
        default=fields.Date.today(),
    )
    qbo_export_limit = fields.Integer(
        string='Export Limit',
        default=10,
        required=True,
    )
    qbo_next_call_point = fields.Datetime(
        string='Next Export Point',
        compute='_compute_next_call',
    )
    qbo_default_stock_valuation_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Default Stock Valuation Account',
        help="""Select here account that will be used for products that are Storable,
        but there 'Inventory Valuation' method is set to Manual.
        We need it cause quickbooks required this account for Stockable products.""",
    )
    qbo_default_write_off_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Default Write-off Account',
        help="""Write-off account is used to record difference between payment downloaded from QBO
        and Invoice total in Odoo in case QBO Invoice is marked as Paid and we also need
        to closed it on Odoo side.""",
    )
    qbo_sync_product = fields.Boolean(
        string='Sync Products',
        default=True,
    )
    qbo_sync_product_category = fields.Boolean(
        string='Sync Products as Category',
    )
    qbo_sync_storable_to_consumable = fields.Boolean(
        string='Sync Storable Product as Consumable',
    )
    qbo_export_out_invoice = fields.Boolean(
        string='Export Customer Invoices (and related Customer Payments)',
        default=True,
    )
    qbo_export_out_refund = fields.Boolean(
        string='Export Customer CreditNotes',
        default=True,
    )
    qbo_export_in_invoice = fields.Boolean(
        string='Export Vendor Bills (and Related Vendor Payments)',
        default=True,
    )
    qbo_export_in_refund = fields.Boolean(
        string='Export Vendor Refunds',
        default=True,
    )
    qbo_def_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Default Journal',
    )

    def initial_import_from_qbo(self):
        """Make initial import from Intuit."""
        self.env['qbo.map.partner'].get_data_from_qbo()
        self.env['qbo.map.product'].get_data_from_qbo()
        self.env['qbo.map.account'].get_data_from_qbo()
        self.env['qbo.map.tax'].get_data_from_qbo()
        self.env['qbo.map.taxcode'].get_data_from_qbo()
        self.env['qbo.map.term'].get_all_data_from_qbo()
        self.env['qbo.map.payment.method'].get_all_data_from_qbo()
        self.env['qbo.map.department'].get_all_data_from_qbo()

    def ensure_qbo_us_company(self):
        if not self.intuit_is_us_company():
            raise UserError(_(
                'This feature is allowed only for US Intuit company.'
            ))

    def external_currency_belong_company(self, currency_name):
        return self.currency_id.name == currency_name

    def _compute_next_call(self):
        cron = self.env.ref(
            'quickbooks_sync_online.trigger_invoice_to_qbo_cron',
            raise_if_not_found=False,
        )
        if cron:
            for rec in self:
                rec.qbo_next_call_point = cron.nextcall

    @api.depends('qbo_auth_url')
    def _compute_redirect_uri(self):
        base_url = self.env['ir.config_parameter']\
            .with_user(SUPERUSER_ID).get_param('web.base.url')
        redirect_uri = '%s/qbo/callback' % base_url

        for rec in self:
            rec.qbo_redirect_uri = redirect_uri

    @api.depends('access_token_update_point')
    def _compute_access_token_cron_point(self):
        cron = self.env.ref(
            'quickbooks_sync_online.refresh_qbo_access_token_cron',
            raise_if_not_found=False,
        )
        if cron:
            for rec in self:
                rec.access_token_cron_point = cron.nextcall

    def get_qbo_invoice_allowed_types(self):
        allowed_types = []
        self_su = self.with_user(SUPERUSER_ID)

        if self_su.qbo_export_out_invoice:
            allowed_types.append('out_invoice')
        if self_su.qbo_export_out_refund:
            allowed_types.append('out_refund')
        if self_su.qbo_export_in_invoice:
            allowed_types.append('in_invoice')
        if self_su.qbo_export_in_refund:
            allowed_types.append('in_refund')

        return allowed_types

    def get_qbo_payment_options(self):
        partner_types, payment_types = [], []

        if self.qbo_export_out_invoice:
            partner_types.append('customer')
            payment_types.append('inbound')
        if self.qbo_export_in_invoice:
            partner_types.append('supplier')
            payment_types.append('outbound')

        return partner_types, payment_types

    def _qbo_auth_client(self, skip_token=False):
        client_id = self.qbo_client_id
        client_secret = self.qbo_client_secret
        redirect_uri = self.qbo_redirect_uri

        if not all((client_id, client_secret, redirect_uri)):
            raise ValidationError(_(
                '"Client ID" or "Client Secret" or "Redirect URI" are not defined.'
            ))
        if not self.qbo_csrf_token:
            self.write({
                'qbo_csrf_token': generate_token() + '.' + str(self.id),
            })
        params = {
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'access_token': self.qbo_access_token,
            'environment': self.get_qbo_env(),
            'state_token': self.qbo_csrf_token,
        }
        if skip_token:
            params.pop('access_token')

        return AuthClient(**params)

    def _generate_qbo_auth_url(self):
        auth_client = self._qbo_auth_client(skip_token=True)

        self.write({
            'qbo_auth_url': auth_client.get_authorization_url([Scopes.ACCOUNTING]),
        })

    def _prepare_subscribers(self):
        self.ensure_one()
        group = self.env.ref(
            'quickbooks_sync_online.qbo_security_group_manager',
            raise_if_not_found=False,
        )
        if not group:
            return None
        users = self.env['res.users'].search([('groups_id', '=', group.id)])\
            .filtered(lambda r: self.id in r.company_ids.ids)
        return users.mapped('partner_id').ids

    def _check_qbo_auth(self):
        self.ensure_one()
        self_su = self.with_user(SUPERUSER_ID)

        if not all((self_su.is_authenticated, self_su.is_authorized)):
            self_su._refresh_qbo_access_token()

        if not all((self_su.is_authenticated, self_su.is_authorized)):
            raise ValidationError(_(
                'You need to authorize your QuickBooks app!'
            ))

    def _check_qbo_product_settings(self):
        self.ensure_one()
        info = None

        if self.qbo_sync_product_category:
            info = _(
                'This operation is not allowed. Your administrator set products synchronization '
                'as synchronization of the corresponding Product category in Quickbooks Settings.'
            )
        elif not self.qbo_sync_product:
            info = _(
                'This operation is not allowed. Your administrator turned off '
                'products synchronization in Quickbooks Settings.'
            )

        if info:
            raise UserError(info)

    def _check_qbo_tax_settings(self):
        self.ensure_one()
        info = None

        if not self.qbo_sync_product:
            info = _(
                'Auto calculation of QBO taxes cannot be used. '
                'Your administrator turned off products synchronisation in Quickbooks Settings.'
            )

        if info:
            raise UserError(info)

    def _search_to_qbo_payments(self):
        self.ensure_one()
        partner_types, payment_types = self.get_qbo_payment_options()

        payments = self.env['account.payment'].search([
            ('state', '=', 'posted'),
            ('company_id', '=', self.id),
            ('qbo_state', '!=', 'proxy'),
            ('partner_type', 'in', partner_types),
            ('date', '>=', self.qbo_export_date_point),
            ('payment_type', 'in', payment_types),
        ])
        # Filter any refunds
        pay_cust_inv = payments.filtered(
            lambda r: r.partner_type == 'customer' and r.payment_type == 'inbound'
        )
        pay_ven_bill = payments.filtered(
            lambda r: r.partner_type == 'supplier' and r.payment_type == 'outbound'
        )
        return pay_cust_inv + pay_ven_bill

    def _search_to_qbo_update(self, model_name):
        records = self.env[model_name].search([
            ('qbo_update_required', '=', True),
        ])
        return records

    @ormcache(
        'self',
        'self.qbo_refresh_token',
        'self.qbo_access_token',
    )
    def get_request_client(self):
        self.ensure_one()
        qbo_company_id = self.qbo_company_id
        qbo_refresh_token = self.qbo_refresh_token

        if not all((qbo_company_id, qbo_refresh_token)):
            raise ValidationError(_(
                '"QBO refresh token" or "QBO company ID" are not defined.'
            ))
        params = {
            'auth_client': self._qbo_auth_client(),
            'company_id': qbo_company_id,
            'refresh_token': qbo_refresh_token,
            'minorversion': MINOR_VERSION,
        }
        return QuickBooks(**params)

    def intuit_is_us_company(self):
        """Check if Intuit company belong to US."""
        if not self.qbo_company_country_iso:
            raise UserError(_(
                'Origin of the current Intuit Company not defined.'
            ))
        return self.qbo_company_country_iso == 'US'

    def get_qbo_env(self):
        """Using Intuit company for production or developing."""
        if not self.qbo_environment:
            self.write({
                'qbo_environment': 'production',
            })
        return self.qbo_environment

    @staticmethod
    def _partner_to_pay_type(partner_type):
        routes = {
            'customer': 'payment',
            'supplier': 'billpayment',
        }
        return routes[partner_type]

    @staticmethod
    def _pay_type_to_partner(pay_type):
        routes = {
            'payment': 'customer',
            'billpayment': 'supplier',
        }
        return routes[pay_type]

    def import_intuit_payments_cron(self):
        """Get new payments from Intuit Company."""
        all_companies = self.env['res.company'].with_user(SUPERUSER_ID).search([])
        companies = all_companies.filtered(
            lambda r: r.is_authorized and r.is_authenticated and r.qbo_payment_sync_in
        )
        MapPayment, result = self.env['qbo.map.payment'], []

        for company in companies:
            partner_types, __ = company.get_qbo_payment_options()

            for p_type in set(partner_types):
                map_type = company._partner_to_pay_type(p_type)
                map_pays = MapPayment.get_intuit_payments(map_type, company)
                result.append((company.name, map_pays))

        _logger.info('QBO imported payments: %s' % result)
        return result

    def export_intuit_payments_cron(self):
        """Export new payments to the Intuit Company."""
        all_companies = self.env['res.company'].with_user(SUPERUSER_ID).search([])
        companies = all_companies.filtered(
            lambda r: r.is_authorized and r.is_authenticated and r.qbo_payment_sync_out
        )
        for company in companies:
            payments = company._search_to_qbo_payments()
            partner_types = payments.mapped('partner_type')
            map_types = [company._partner_to_pay_type(p) for p in set(partner_types)]

            export_dict, __ = payments._collect_qbo_export_dict(map_types, company)
            company._process_qbo_export_dict(export_dict)

        return True

    def update_records_to_intuit(self):
        """Update records to the Intuit Company."""
        all_companies = self.env['res.company'].with_user(SUPERUSER_ID).search([])
        companies = all_companies.filtered(lambda r: r.is_authorized and r.is_authenticated)
        if not companies:
            return

        for model_name in MODELS_TO_UPDATE:
            records = self._search_to_qbo_update(model_name)

            for map_type in self.env[model_name].map_types:
                for company in companies:
                    records_to_update = self.env[model_name]
                    for rec in records:
                        map_rec = rec._get_qbo_map_instance(map_type, company.id)
                        if len(map_rec) == 1:
                            records_to_update |= rec
                    if records_to_update:
                        records_to_update._update_records_to_qbo(company)

        return True

    def export_invoices_to_qbo_cron(self):
        self._compute_next_call()
        all_companies = self.env['res.company'].with_user(SUPERUSER_ID).search([])
        companies = all_companies.filtered(
            lambda r: r.is_authorized and r.is_authenticated and r.qbo_auto_export
        )

        for company in companies:
            limit = company.qbo_export_limit
            move_types = company.get_qbo_invoice_allowed_types()

            invoices = self.env['account.move'].search(
                [
                    ('invoice_date', '>=', company.qbo_export_date_point),
                    ('company_id', '=', company.id),
                    ('state', '=', 'posted'),
                    ('qbo_state', '!=', 'proxy'),
                    ('move_type', 'in', move_types),
                ],
                limit=limit,
                order='invoice_date,id',
            )

            trouble_invoices = invoices.filtered(lambda r: r.qbo_state != 'todo')

            if len(trouble_invoices) >= limit:
                info = _(
                    'QuickBooks Job has not been created due to there are '
                    'previous exports troubles. Fix them first please.'
                )
                _logger.warning(info)
                invoices._make_message_post(info, company)
                continue

            export_dict, __ = invoices._collect_qbo_export_dict(company)
            company._process_qbo_export_dict(export_dict)

        return True

    def _revoke_qbo_access(self):
        if all((self.qbo_client_id, self.qbo_client_secret, self.qbo_refresh_token)):
            try:
                client = self._qbo_auth_client()
                client.revoke(token=self.qbo_refresh_token)
            except AuthClientError as ex:
                _logger.error(ex.args)

        res = self.write(QBO_FIELDS_TO_ERASE)
        self.clear_caches()
        _logger.info('QBO access has been revoked.')
        return res

    def _refresh_qbo_access_token(self):
        _logger.info('Trying to update QBO access token.')
        if not all((self.qbo_refresh_token, self.qbo_client_id, self.qbo_client_secret)):
            _logger.error('QBO access token may not be updated.')
            return False

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': get_auth_header(self.qbo_client_id, self.qbo_client_secret),
        }
        body = {
            'grant_type': 'refresh_token',
            'refresh_token': self.qbo_refresh_token,
        }
        response = requests.post(ACCESS_TOKEN_URL, data=urlencode(body), headers=headers)
        if response.status_code != 200:
            _logger.error(
                'Access Token update error: %s, %s.' % (response.status_code, response.text)
            )
            self.write(COMPANY_FIELDS_TO_RESET)
            return False

        json_response = response.json()
        access_delta = json_response.get('expires_in', False)
        refresh_delta = json_response.get('x_refresh_token_expires_in', False)
        vals = {
            'is_authorized': True,
            'is_authenticated': True,
            'qbo_access_token': json_response.get('access_token'),
            'qbo_refresh_token': json_response.get('refresh_token'),
            'access_token_update_point': datetime.now() + timedelta(seconds=access_delta),
            'refresh_token_update_point': datetime.now() + timedelta(seconds=refresh_delta),
        }
        res = self.write(vals)
        self.clear_caches()
        _logger.info('QBO Access Token has been successfully updated.')
        return res

    def _update_intuit_company_info(self):
        self.ensure_one()
        company_info = self._fetch_qbo_company_info()

        if not company_info.validate_country():
            raise ValidationError(_(
                'Different countries for Odoo company and QuickBooks company are not allowed!'
            ))

        if not company_info.validate_home_currency():
            raise ValidationError(_(
                'Different currencies for Odoo company and QuickBooks company are not allowed!'
            ))

        self.write({
            'qbo_company_info': company_info.address_format(),
            'qbo_company_country_iso': company_info.country_iso,
        })
        return company_info

    def refresh_qbo_access_token(self):
        all_companies = self.env['res.company'].with_user(SUPERUSER_ID).search([])
        companies = all_companies.filtered(
            lambda r: r.qbo_client_id and r.qbo_client_secret and r.qbo_refresh_token
        )
        results = list()
        for company in companies:
            res = company._refresh_qbo_access_token()
            results.append(res)
        return results

    def _fetch_qbo_company_info(self):
        try:
            client = self.get_request_client()
            preference = Preferences.get(qb=client)
            currency_list = CompanyCurrency.all(qb=client)
            company_info = CompanyInfo.get(self.qbo_company_id, qb=client)
        except Exception as ex:
            raise ValidationError(ex.args[0])

        return QboCompanyInfo(self, preference, company_info, currency_list)

    def _process_qbo_export_dict(self, export_dict):
        """
        export_dict = {
            'res.partner': {
                'vendor': [res.partner(1,), res.partner(6,), res.partner(7,)],
                'customer': [res.partner(2,), res.partner(6,), res.partner(8,)],
            },
            'product.product': {
                'item': [product.product(2,), product.product(14,), product.product(21,)],
            },
            'account.move': {
                'invoice': [account.move(1,), account.move(2,)],
                'creditmemo': [account.move(3,), account.move(5,)],
                'bill': [account.move(4,), account.move(7,)],
                'vendorcredit': [account.move(6,), account.move(8,)],
            },
            'account.payment': {
                'payment': [account.payment(5,), account.payment(8,)],
                'billpayment': [account.payment(2,), account.payment(3,), account.payment(4,)],
            }
        }
        """
        self.ensure_one()

        common_ctx = dict()
        if self.env.context.get('qbo_plain_export'):
            common_ctx['test_queue_job_no_delay'] = True

        for _name in MODELS_TO_EXPORT.keys():
            for map_type, model_ids_list in export_dict.get(_name, {}).items():
                grouped_records = self._model_ids_list_split_by_context(model_ids_list)

                for model_ids, ctx_tuple in grouped_records:
                    model_ids.with_context(**common_ctx)\
                        ._export_qbo_batch(map_type, self, dict(ctx_tuple))

        return True

    def _model_ids_list_split_by_context(self, model_ids_list):
        """
        input:
            model_ids_list = [
                res.partner(33,), res.partner(26,), res.partner(14,), res.partner(27,),
            ]

        output:
            [
                (res.partner(33, 26, 14), ()), (res.partner(27,), (('ensure_qbo_currency', True),)),
            ]

        """
        rec_with_ctx, rec_without_ctx = set(), set()

        for record in model_ids_list:
            ctx_tuple = record._extract_essential_context()
            if ctx_tuple:
                rec_with_ctx.add((record, ctx_tuple))
            else:
                rec_without_ctx.add(record)

        rec_without_ctx = rec_without_ctx\
            and [(reduce(lambda x, y: x + y, set(rec_without_ctx)), tuple())]

        return list(rec_without_ctx) + list(rec_with_ctx)
