# Copyright 2020 VentorTech OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from ..utils import QboClass, IntuitResponse
from odoo import models, fields, _
from odoo.exceptions import UserError, ValidationError

import logging
from datetime import datetime as dt
from collections import namedtuple
from dateutil import parser

_logger = logging.getLogger(__name__)

try:
    from quickbooks.objects.payment import Payment
    from quickbooks.objects.billpayment import BillPayment
    from quickbooks.helpers import qb_datetime_format
except (ImportError, IOError) as ex:
    _logger.error(ex)

INVOICE = 'Invoice'
CREDITMEMO = 'CreditMemo'
BILL = 'Bill'
VENDORCREDIT = 'VendorCredit'


class QboMapPayment(models.Model):
    _name = 'qbo.map.payment'
    _inherit = 'qbo.map.mixin'
    _description = 'Qbo Map Payment'

    _qbo_lib_class = QboClass(Payment, BillPayment)

    _res_model = 'account.payment'
    _related_field = 'payment_id'
    _reverse_field = 'qbo_payment_ids'
    _map_routes = {
        'qbo_name': ('["CustomerRef"]["name"]', ''),
        'currency_ref': ('["CurrencyRef"]["value"]', ''),
        'pay_method': ('["PaymentMethodRef"]["value"]', ''),
        'txn_date': ('["TxnDate"]', ''),
        'sync_token': ('["SyncToken"]', '0'),
        'update_point.update_time_str': ('["MetaData"]["LastUpdatedTime"]', ''),
        'update_point.create_time_str': ('["MetaData"]["CreateTime"]', ''),
    }

    txn_id = fields.Many2one(
        comodel_name='qbo.map.account.move',
        string='Map Invoice',
        ondelete='restrict',
    )
    invoice_id = fields.Many2one(
        related='txn_id.invoice_id',
    )
    txn_type = fields.Selection(
        related='txn_id.qbo_lib_type',
        string='Map Invoice Type',
    )
    txn_amount = fields.Char(
        string='Amount',
    )
    txn_date = fields.Char(
        string='Date',
    )
    pay_method = fields.Char(
        string='Payment Method',
    )
    currency_ref = fields.Char(
        string='Currency',
    )
    payment_id = fields.Many2one(
        comodel_name=_res_model,
        string='Odoo Payment',
        readonly=True,
    )
    sync_token = fields.Char(
        string='Sync Token',
        size=3,
        default='0',
        help='Sync token increments after payment update.',
    )
    update_point = fields.Datetime(
        string='Update Time Point',
        readonly=True,
    )

    def try_to_map(self, *args, **kw):
        raise NotImplementedError()

    @property
    def pay_context(self):
        return {
            'active_model': self.invoice_id._name,
            'active_ids': self.invoice_id.ids,
        }

    @staticmethod
    def datetime_field_name(map_type):
        routes = {
            'payment': 'qbo_cus_pay_point',
            'billpayment': 'qbo_ven_pay_point',
        }
        return routes[map_type]

    def register_payment(self):
        """Odoo Registration of the received payment."""
        records = self.filtered('txn_id.invoice_id')\
            .sorted(lambda r: r.update_point or dt.now())
        return [(rec.qbo_id, rec._register_payment()) for rec in records]

    def get_intuit_payments(self, map_type, company):
        """Getting the latest payments from the Intuit Company."""
        start_point = self.get_fetch_point(map_type, company)

        if not start_point:
            _logger.info(_(
                'There are no exported invoices for payments synchronizations for "%s".'
                % company.name
            ))
            return False

        condition = self._get_fetch_condition(start_point)
        result, code, = self._fetch_qbo_by_query(company, map_type, condition)

        if code != IntuitResponse.SUCCESS:
            _logger.error(result)
            return False

        if not result:
            _logger.info(_(
                'There are no new Intuit payments for "%s".' % company.name
            ))
            return False

        payments = self._handle_received_records(result, map_type, company.id)

        self._update_fetch_point(result, map_type, company)

        if payments and not self.env.context.get('not_register_payment'):
            job_kwargs = dict(
                priority=20,
                description='Register received QBO payments',
            )
            payments.with_delay(**job_kwargs).register_payment()

        return payments

    def get_pay_method_journal(self):
        self.ensure_one()
        if self.pay_method:
            qbo_method = self.env['qbo.map.payment.method'].search([
                ('qbo_id', '=', self.pay_method),
                ('company_id', '=', self.company_id.id),
            ], limit=1)
            journal = qbo_method.journal_id
        else:
            journal = self.company_id.qbo_def_journal_id

        return journal

    def get_fetch_point(self, map_type, company):
        date_field = self.datetime_field_name(map_type)
        date_field_value = getattr(company, date_field)

        if self._parse_datetime_from_str(date_field_value):
            return date_field_value

        condition = self._get_datetime_condition(date_field, company.id)

        self.env.cr.execute(condition)
        result = self.env.cr.fetchone()
        point = result[0] and result[0].replace(minute=0, hour=0, second=0, microsecond=0)

        return self._convert_datetime_to_str(point)

    def unlink(self):
        if self.filtered('payment_id'):
            raise UserError(_(
                'Registered payments "%s" may not be deleted!' % self.filtered('payment_id').ids
            ))
        return super(QboMapPayment, self).unlink()

    @staticmethod
    def _retrieve_payment_options(invoice_type):
        routes = {
            'invoice': ('customer', 'inbound'),
            'creditmemo': ('customer', 'outbound'),
            'bill': ('supplier', 'outbound'),
            'vendorcredit': ('supplier', 'inbound'),
        }
        return routes[invoice_type]

    @staticmethod
    def _get_datetime_condition(date_field, company_id):
        routes = {
            'qbo_cus_pay_point': ('invoice', 'creditmemo'),
            'qbo_ven_pay_point': ('bill', 'vendorcredit'),
        }
        query_string = """
        SELECT MIN(create_date) FROM qbo_map_account_move
        WHERE company_id = %s AND (qbo_lib_type = '%s' OR qbo_lib_type = '%s')
        """
        return query_string % (company_id, *routes[date_field])

    @staticmethod
    def _get_fetch_condition(*params):
        return "MetaData.LastUpdatedTime >= '%s' ORDERBY MetaData.LastUpdatedTime ASC" % params

    @staticmethod
    def _parse_pay_line(line):
        try:
            txn = line['LinkedTxn']
            map_invoice_id = txn[0]['TxnId']
            invoice_type = txn[0]['TxnType'].lower()
            amount = line['Amount']
        except Exception as ex:
            _logger.error(ex)
            return []

        line_args = [map_invoice_id, invoice_type, amount]
        return line_args if all(line_args[1:]) else []

    @staticmethod
    def _parse_datetime_from_str(dtime_str):
        try:
            datetime_ = parser.isoparse(dtime_str).replace(tzinfo=None)
        except Exception:
            return False
        return datetime_

    @staticmethod
    def _convert_datetime_to_str(dtime_obj):
        try:
            datetime_ = qb_datetime_format(dtime_obj)
        except Exception:
            return False
        return datetime_

    @staticmethod
    def _roll_up_args(args_list):
        Pay = namedtuple('Pay', 'txn_id txn_type amount')
        return [Pay(*args) for args in args_list]

    def _parse_payment_dict(self, object_dict):
        line_args_list = [
            self._parse_pay_line(line) for line in object_dict.get('Line', [])
        ]
        return self._roll_up_args(filter(bool, line_args_list))

    def _create_map_one(self, qbo_lib_model, extra_vals, **kw):
        """Redefined method from abstract model."""
        company_id = self.env.context.get('apply_company')
        if not company_id:
            raise ValidationError(_(
                'Company not defined during creating map-object.'
            ))

        if self.env.context.get('force_save_qbo_record'):
            extra_vals.update({
                'txn_id': self.env.context.get('_txn_id', False),
                'txn_amount': self.env.context.get('_txn_amount', False),
            })
            return super(QboMapPayment, self)._create_map_one(qbo_lib_model, extra_vals, **kw)

        qbo_id = qbo_lib_model.Id
        map_type = qbo_lib_model.qbo_object_name.lower()

        base_vals = {
            'qbo_id': qbo_id,
            'qbo_lib_type': map_type,
            'company_id': company_id,
            'qbo_object': qbo_lib_model.to_json(),
            **extra_vals,
            **self._parse_values_from_lib_obj(qbo_lib_model),
        }
        map_vals = self._adjust_map_values(base_vals, qbo_lib_model)

        previous_pays = self.search([
            ('qbo_id', '=', qbo_id),
            ('qbo_lib_type', '=', map_type),
            ('company_id', '=', company_id),
        ])

        transaction_list = self._parse_payment_dict(qbo_lib_model.to_dict())

        if previous_pays:
            tokens_list = [int()]
            tokens_list.extend(
                previous_pays.filtered('sync_token').mapped('sync_token')
            )
            if int(map_vals['sync_token']) <= max(map(int, tokens_list)):
                # Return if `sync_token` was not incremented.
                _logger.info('%s-object was skipped: [%s].' % (map_type.capitalize(), qbo_id))
                return self.browse()

            to_create_list = self._collect_vals_from_transactions(
                previous_pays,
                transaction_list,
                map_vals,
            )
        else:
            to_create_list = [
                self._collect_single_pay_vals(pay, map_vals) for pay in transaction_list
            ]

        to_create_list = [x for x in to_create_list if x]

        if not to_create_list:
            return self.browse()

        map_ones = self.create(to_create_list)
        _logger.info('Map %s-object "%s" was created.' % (map_type, map_ones.ids))
        return map_ones

    def _collect_vals_from_transactions(self, previous_pays, txn_list, vals):
        def _update_vals(pay):
            exists_pays = previous_pays.filtered(
                lambda r: r.txn_id.qbo_id == pay.txn_id and r.txn_type == pay.txn_type
            )
            paid_sum = sum(map(float, exists_pays.mapped('txn_amount')))
            balance_amount = round(float(pay.amount) - paid_sum, 2) if exists_pays else pay.amount
            return {**vals, **{'txn_amount': str(balance_amount)}}

        return [
            self._collect_single_pay_vals(pay, _update_vals(pay)) for pay in txn_list
        ]

    def _collect_single_pay_vals(self, pay, vals):
        map_invoice = self.env['qbo.map.account.move'].search([
            ('invoice_id', '!=', False),
            ('qbo_id', '=', pay.txn_id),
            ('payment_state', 'not in', ('paid', 'in_payment')),
            ('qbo_lib_type', '=', pay.txn_type),
            ('company_id', '=', vals['company_id']),
        ], limit=1)

        if not map_invoice:
            return dict()

        _map_vals = {
            'txn_id': map_invoice.id,
            'txn_amount': pay.amount,
            **vals,  # `vals` have to be unpacked right here
        }
        return _map_vals

    def _adjust_map_values(self, vals, qbo_lib_model):
        res = super(QboMapPayment, self)._adjust_map_values(vals, qbo_lib_model)

        upd_time_str = res['update_point']['update_time_str']
        crt_time_str = res['update_point']['create_time_str']
        time_to_convert = upd_time_str or crt_time_str

        res['update_point'] = self._parse_datetime_from_str(time_to_convert)

        if qbo_lib_model.qbo_object_name == 'BillPayment':
            res['qbo_name'] = qbo_lib_model.VendorRef.name

        return res

    def _retrieve_amount_vals(self, map_invoice):
        self.ensure_one()
        vals, pay_ids = {'amount': abs(float(self.txn_amount))}, []

        if map_invoice.qbo_object_name == INVOICE:
            pay_ids = [
                pay.TxnId for pay in map_invoice.LinkedTxn if pay.TxnType == 'Payment'
            ]
        elif map_invoice.qbo_object_name == BILL:
            pay_ids = [
                pay.TxnId for pay in map_invoice.LinkedTxn if pay.TxnType == 'BillPaymentCheck'
            ]
        elif map_invoice.qbo_object_name == VENDORCREDIT:
            pass  # TODO: It seems there is no smt related to payments
        elif map_invoice.qbo_object_name == CREDITMEMO:
            pass  # TODO: CreditMemo object has no LinkedTxn list

        pay_ids.sort(key=int)

        if pay_ids and self.qbo_id == pay_ids[-1] and map_invoice.Balance == 0:
            self.txn_id.write({
                'qbo_object': map_invoice.to_json(),
            })

            write_off_account_id = self.company_id.qbo_default_write_off_account_id

            if not write_off_account_id:
                info = _(
                    'It’s not possible to register payment in Odoo. '
                    'Specify `Default Write-off Account` in the module settings.'
                )
                raise ValidationError(info)

            vals.update({
                'payment_difference_handling': 'reconcile',
                'writeoff_account_id': write_off_account_id.id,
            })

        return vals

    def _register_payment(self):
        if self.payment_id:
            _logger.info('Current payment has already registered.')
            return False

        map_invoice = self.txn_id

        if not map_invoice or map_invoice.payment_state in ('paid', 'in_payment'):
            _logger.info('Related Odoo invoice was already marked as Paid.')
            return False

        result, code = map_invoice._fetch_qbo_one_by_id(
            map_invoice.company_id,
            map_invoice.qbo_lib_type,
            map_invoice.qbo_id,
        )

        if code != IntuitResponse.SUCCESS:
            _logger.error('Payment registration were skipped.')
            return False

        payment_journal = self.get_pay_method_journal()

        if not payment_journal:
            info = _(
                'It is not possible to register payment in Odoo. Please, ask Administrator '
                'to check: (1) In menu [QuickBook Online --> Configuration --> Settings] define '
                '"Default Payment Journal" (2) In menu '
                '[QuickBook Online --> Mapping --> Payment Methods] make sure to specify '
                '"Related Journal" for every payment method.'
            )
            raise ValidationError(info)

        from_cur = self.env['res.currency'].search([
            ('name', '=', self.currency_ref),
        ], limit=1)

        payment_vals = {
            'journal_id': payment_journal.id,
            'currency_id': (from_cur or self.invoice_id.currency_id).id,
            'payment_date': dt.strptime(self.txn_date, '%Y-%m-%d').date(),
        }
        payment_vals.update(
            self._retrieve_amount_vals(result)
        )
        ac_pay_reg = self.env['account.payment.register']\
            .with_context(**self.pay_context).create(payment_vals)

        payment = ac_pay_reg._create_payments()

        self.write({
            'payment_id': payment.id,
        })
        self.invoice_id.with_company(self.company_id).write({
            'qbo_transaction_info': False,
        })
        return payment

    def _update_fetch_point(self, lst, map_type, company):
        update_time_list = [x.MetaData.get('LastUpdatedTime', False) for x in lst]
        filter_list = list(filter(bool, update_time_list))

        if filter_list:
            company.write({
                self.datetime_field_name(map_type): filter_list[-1],
            })
