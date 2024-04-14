# Copyright 2020 VentorTech OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from .utils import handle_operational_error
from .mapping.qbo_map_payment import INVOICE, CREDITMEMO, BILL, VENDORCREDIT

from odoo import models, fields, _
from odoo.exceptions import ValidationError

import json
import logging
from collections import defaultdict

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _name = 'account.payment'
    _inherit = ['account.payment', 'qbo.transaction.mixin', 'job.transaction.mixin']

    _qbo_map = 'qbo.map.payment'

    qbo_payment_ids = fields.One2many(
        comodel_name=_qbo_map,
        inverse_name='payment_id',
        string='QBO Payment',
        readonly=True,
    )

    def export_payment_to_qbo(self):
        """Export payments to the Intuit company."""
        company = self.define_transaction_company()
        company._check_qbo_auth()

        partner_types, payment_types = company.get_qbo_payment_options()

        if not (partner_types and payment_types):
            _logger.info('There are no payments for export.')
            return

        payments = self.filtered(
            lambda r: r.qbo_state != 'proxy'
            and r.partner_type in partner_types
            and r.payment_type in payment_types
            and r.company_id == company
        )
        # Filter any refunds
        pay_cust_inv = payments.filtered(
            lambda r: r.partner_type == 'customer' and r.payment_type == 'inbound'
        )
        pay_ven_bill = payments.filtered(
            lambda r: r.partner_type == 'supplier' and r.payment_type == 'outbound'
        )
        pays = pay_cust_inv + pay_ven_bill

        if not pays:
            _logger.info('There are no draft payments for export.')
            return

        partner_types = payments.mapped('partner_type')
        map_types = [company._partner_to_pay_type(p) for p in set(partner_types)]

        export_dict, __ = pays.with_context(raise_exception=True)\
            ._collect_qbo_export_dict(map_types, company)

        return company._process_qbo_export_dict(export_dict)

    @property
    def pay_qbo_invoice_type(self):
        self.ensure_one()
        routes = {
            ('customer', 'inbound'): 'invoice',
            ('customer', 'outbound'): 'creditmemo',
            ('supplier', 'outbound'): 'bill',
            ('supplier', 'inbound'): 'vendorcredit',
        }
        return routes.get((self.partner_type, self.payment_type), False)

    @property
    def qbo_reconciled_ids(self):
        self.ensure_one()
        routes = {
            'customer': 'reconciled_invoice_ids',
            'supplier': 'reconciled_bill_ids',
        }
        return getattr(self, routes[self.partner_type])

    def _prepare_pay_ref_number(self):
        name = self.name
        txn_id = self.env.context.get('_txn_id')
        if txn_id:
            name = f'{txn_id}-{name}'
        return name[:21]

    def _get_condition_for_check_external(self, qbo_lib_model):
        if qbo_lib_model.qbo_object_name == 'BillPayment':
            return f"DocNumber = '{qbo_lib_model.DocNumber}'"
        return f"PaymentRefNum = '{qbo_lib_model.PaymentRefNum}'"

    def _create_qbo_payment_line(self, invoice, amount):
        routes = {
            'invoice': INVOICE,
            'creditmemo': CREDITMEMO,
            'bill': BILL,
            'vendorcredit': VENDORCREDIT,
        }
        map_invoice = invoice.qbo_invoice_ids

        pay_line_dict = {
            'Amount': amount,
            'LinkedTxn': [{
                'TxnId': map_invoice.qbo_id,
                'TxnType': routes[map_invoice.qbo_lib_type],
            }],
        }
        return [pay_line_dict]

    def _set_qbo_values(self, qbo_lib_model, company, invoice, amount, **kw):
        self.ensure_one()

        routes = {
            'customer': 'customer',
            'supplier': 'vendor',
        }
        partner_type = routes[self.partner_type]
        qbo_map_partner = self.partner_id._get_qbo_map_instance(partner_type, company.id)
        partner_ref = {
            'value': qbo_map_partner.qbo_id or '',
        }

        if partner_type == 'customer':
            qbo_lib_model.CustomerRef = partner_ref
            qbo_lib_model.PaymentRefNum = self._prepare_pay_ref_number()

            qbo_pay_method = self.journal_id.get_qbo_related_method(company.id)
            qbo_lib_model.PaymentMethodRef = {
                'value': qbo_pay_method.qbo_id or '',
            }
        else:
            qbo_lib_model.VendorRef = partner_ref
            qbo_lib_model.PayType = 'Check'  # We are not supporting `CreditCard` for now
            qbo_lib_model.DocNumber = self._prepare_pay_ref_number()

            account = self.journal_id.default_account_id
            qbo_map_account = account.get_qbo_related_account(company.id)

            qbo_lib_model.CheckPayment = {
                'BankAccountRef': {
                    'value': qbo_map_account.qbo_id or '',
                }
            }

        qbo_lib_model.TotalAmt = amount
        qbo_lib_model.CurrencyRef = {'value': self.currency_id.name}
        qbo_lib_model.TxnDate = self.date.strftime('%Y-%m-%d')

        qbo_lib_model.Line = self._create_qbo_payment_line(invoice, amount)

    def _perform_and_force_save(self, map_type, company, invoice, amount):
        self.ensure_one()
        qbo_lib_model = self._init_qbo_lib_class(map_type)
        self._set_qbo_values(qbo_lib_model, company, invoice, amount)
        ctx = {
            'force_save_qbo_record': True,
            '_txn_amount': amount,
            '_txn_id': invoice.qbo_invoice_ids.id,
        }
        return self.with_context(**ctx)._perform_export_one(qbo_lib_model, company)

    def _export_one_object_to_many(self, map_type, company):
        self.ensure_one()
        total_amount = self.amount
        last_index = len(self.qbo_reconciled_ids)

        for idx, invoice in enumerate(self.qbo_reconciled_ids, start=1):
            apply_amount = False
            invoice_payments_widget = json.loads(invoice.invoice_payments_widget)

            for dct in invoice_payments_widget.get('content', []):
                if dct.get('account_payment_id') == self.id:
                    apply_amount = dct.get('amount')
                    break

            if apply_amount:
                total_amount -= apply_amount
                if idx == last_index and total_amount > 0:
                    apply_amount += total_amount

                self._perform_and_force_save(map_type, company, invoice, apply_amount)

    @handle_operational_error
    def _export_one_object(self, map_type, company, check_external=False):
        self.ensure_one()
        self = self.with_context(qbo_check_external=check_external)

        if len(self.qbo_reconciled_ids) > 1:
            return self._export_one_object_to_many(map_type, company)

        return self._perform_and_force_save(
            map_type, company, self.qbo_reconciled_ids, self.amount)

    def _check_requirements(self, company, allowed_invoice_ids):
        self.ensure_one()
        if not self.qbo_reconciled_ids:
            raise ValidationError(_(
                'There is no related invoice for the payment "%s".' % self.name
            ))

        invoice_type = self.pay_qbo_invoice_type

        for invoice in self.qbo_reconciled_ids:
            map_invoice = invoice._get_map_instance_or_raise(
                invoice_type, company.id, raise_if_not_found=False)
            if not map_invoice and (invoice.id not in allowed_invoice_ids):
                raise ValidationError(_(
                    'Not the all required nested exports were launched. Fix them first.\n'
                    'In the related invoice "%s" you can read it in the greater details.'
                    % invoice.display_name
                ))

        if self.partner_type == 'customer':
            self.journal_id.get_qbo_related_method(company.id)
        else:
            account = self.journal_id.default_account_id
            account.get_qbo_related_account(company.id)

    def _validate_qbo_type_export(self, map_type, company, allowed_invoice_ids):
        _logger.info('Validate "%s" to export "%s". Redefined' % (map_type, self.ids))
        self.ensure_one()
        raise_exception = self.env.context.get('raise_exception')
        types_to_export, error_message = [], False

        def _do_raise(info):
            if raise_exception:
                raise ValidationError(info)

        if self._get_qbo_map_instance(map_type, company.id):
            self._write_info('proxy', '', company.id)
        else:
            types_to_export.append(map_type)

        if not types_to_export:
            return types_to_export, error_message

        try:
            self._any_qbo_checking(map_type, company)
            self._check_requirements(company, allowed_invoice_ids)
        except ValidationError as ex:
            _do_raise(ex.args[0])
            error_message = ex.args[0]
            types_to_export.remove(map_type)
            self._write_info('rejected', ex.args[0], company.id)

        return types_to_export, error_message

    def _collect_dict_single_type(self, map_types, company):
        _logger.info('Collect "%s" dict for "%s".' % (str(map_types), self.ids))
        assert len(map_types) == 1
        name, allowed_ids = self._name, []
        ctx = {'raise_exception': self.env.context.get('raise_exception')}
        routes = {
            'payment': 'reconciled_invoice_ids',
            'billpayment': 'reconciled_bill_ids',
        }
        export_dict, allowed_invoice_ids = self.mapped(routes[map_types[0]])\
            .with_context(**ctx)._collect_qbo_export_dict(company)

        for pay in self:

            types_to_export, error_message = pay.with_context(**ctx)\
                ._validate_qbo_type_export(map_types[0], company, allowed_invoice_ids)

            for map_type in types_to_export:
                export_dict[name][map_type].append(pay)

            if error_message:
                pay._write_info('rejected', error_message, company.id)
                continue

            allowed_ids.append(pay.id)

        return export_dict, allowed_ids

    def _collect_qbo_export_dict(self, map_types, company):
        _logger.info('Collect "%s" export dict "%s". Redefined.' % (str(map_types), self.ids))
        export_dict, allowed_ids = defaultdict(lambda: defaultdict(list)), []

        for map_type in map_types:
            partner_type = company._pay_type_to_partner(map_type)
            pays = self.filtered(lambda r: r.partner_type == partner_type)

            dict_single_type, list_ids = pays._collect_dict_single_type([map_type], company)

            for _name, nested_dict in dict_single_type.items():
                for m_type, records in nested_dict.items():
                    export_dict[_name][m_type].extend(records)

            allowed_ids.extend(list_ids)

        return export_dict, allowed_ids
