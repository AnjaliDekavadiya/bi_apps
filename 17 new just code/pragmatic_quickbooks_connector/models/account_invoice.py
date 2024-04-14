# -*- coding: utf-8 -*-
import json
import logging
import re
from datetime import datetime

import requests

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, RedirectWarning

_logger = logging.getLogger(__name__)


class QBOPaymentMethod(models.Model):
    _inherit = 'account.journal'

    qbo_method_id = fields.Char(
        "QBO Id", copy=False, help="QuickBooks database recordset id")

    @api.model
    def get_payment_method_ref(self, qbo_method_id):
        company = self.env['res.users'].search(
            [('id', '=', self._uid)]).company_id
        method = self.search([('qbo_method_id', '=', qbo_method_id)], limit=1)
        # If account is not created in odoo then import from QBO and create.
        if not method:
            url_str = company.get_import_query_url()
            url = url_str.get('url') + '/paymentmethod/' + qbo_method_id
            data = requests.request('GET', url, headers=url_str.get('headers'))
            if data.status_code == 200:
                method = self.create_payment_method(data)
        return method.id

    @api.model
    def create_payment_method(self, data):
        """Import payment method from QBO
        :param data: payment method object response return by QBO
        :return qbo.payment.method: qbo payment method object
        """
        method_obj = False
        res = json.loads(str(data.text))
        _logger.info("Payment method data {}".format(res))
        if 'QueryResponse' in res:
            PaymentMethod = res.get('QueryResponse').get('PaymentMethod', [])
        else:
            PaymentMethod = [res.get('PaymentMethod')] or []
        if len(PaymentMethod) == 0:
            raise UserError(
                "It seems that all of the Payment Method are already imported.")
        for method in PaymentMethod:
            method_obj = self.search(
                [('qbo_method_id', '=', method.get("Id")), ('code', '=', 'QB' + str(method.get("Id")))], limit=1)
            if not method_obj:
                vals = {
                    'name': method.get("Name", ''),
                    'qbo_method_id': method.get("Id"),
                    'active': method.get('Active'),
                    'code': 'QB' + str(method.get("Id")),
                }
                if method.get('Type') == 'CREDIT_CARD':
                    vals.update({'type': 'bank'})
                elif method.get('Type') == 'NON_CREDIT_CARD':
                    vals.update({'type': 'cash'})
                else:
                    vals.update({'type': 'general'})
                method_obj = self.create(vals)
                _logger.info(
                    _("Payment Method created sucessfully! Payment Method Id: %s" % (method_obj.id)))
                company = self.env.user.company_id
                if company.import_payment_method_by_date:
                    date_format = '%Y-%m-%d'
                    if company.paymnt_method_import_by == 'crt_dt':
                        date_string = method.get('MetaData').get(
                            'CreateTime')[:10]
                    else:
                        date_string = method.get('MetaData').get(
                            'LastUpdatedTime')[:10]

                    date_object = datetime.strptime(date_string,
                                                    date_format).date()
                    company.import_payment_method_date = date_object
            else:
                vals = {
                    'name': method.get("Name", ''),
                    'active': method.get('Active'),
                }
                method_obj.write(vals)
                _logger.info(
                    _("Payment Method updated sucessfully! Payment Method Id: %s" % (method_obj.id)))
                company = self.env.user.company_id
                if company.import_payment_method_by_date:
                    date_format = '%Y-%m-%d'
                    if company.paymnt_method_import_by == 'crt_dt':
                        date_string = method.get('MetaData').get(
                            'CreateTime')[:10]
                    else:
                        date_string = method.get('MetaData').get(
                            'LastUpdatedTime')[:10]

                    date_object = datetime.strptime(date_string,
                                                    date_format).date()
                    company.import_payment_method_date = date_object
        return method_obj

    @api.model
    def export_to_qbo(self):
        """Export payment method to QBO"""
        # if self._context.get('method_id'):
        if self._context.get('active_ids'):
            payment_methods = self.browse(self._context.get('active_ids'))
        else:
            payment_methods = self

        access_token = None
        realmId = None
        quickbook_config = self.env['res.users'].search(
            [('id', '=', self._uid)]).company_id
        if quickbook_config.access_token:
            access_token = quickbook_config.access_token
        if quickbook_config.realm_id:
            realmId = quickbook_config.realm_id

        for method in payment_methods:
            vals = {
                'Name': method.name,
            }
            # if method.type:
            #     vals.update({'Type': method.type})
            parsed_dict = json.dumps(vals)

            if access_token:
                headers = {}
                headers['Authorization'] = 'Bearer ' + str(access_token)
                headers['Content-Type'] = 'application/json'
                result = requests.request('POST', quickbook_config.url + str(realmId) + "/paymentmethod",
                                          headers=headers, data=parsed_dict)
                if result.status_code == 200:
                    # response text is either xml string or json string
                    data = re.sub(r'\s+', '', result.text)
                    if (re.match(r'^<.+>$', data)):
                        response = quickbook_config.convert_xmltodict(
                            result.text)
                        response = response.get('IntuitResponse')
                    if (re.match(r'^({|[).+(}|])$', data)):
                        response = json.loads(result.text, encoding='utf-8')
                    if response:
                        # update agency id and last sync id
                        method.qbo_method_id = response.get(
                            'PaymentMethod').get('Id')
                        quickbook_config.last_imported_tax_agency_id = response.get(
                            'PaymentMethod').get('Id')

                    _logger.info(
                        _("%s exported successfully to QBO" % (method.name)))
                else:
                    _logger.error(
                        _("[%s] %s" % (result.status_code, result.reason)))
                    raise ValidationError(
                        _("[%s] %s %s" % (result.status_code, result.reason, result.text)))


class AccountPayment(models.Model):
    _inherit = "account.payment"

    qbo_payment_id = fields.Char(
        "QBO Payment Id", copy=False, help="QuickBooks database recordset id")
    qbo_bill_payment_id = fields.Char(
        "QBO Bill Payment Id", copy=False, help="QuickBooks database recordset id")
    qbo_payment_ref = fields.Char(
        "QBO Payment Ref", help="QBO payment reference")
    qbo_paytype = fields.Selection([('check', 'Check'), ('credit_card', 'Credit Card')], default=False,
                                   string='QBO Pay Type')
    qbo_bankacc_ref_name = fields.Many2one(
        'account.account', string='Bank Account Reference Name')
    qbo_cc_ref_name = fields.Many2one(
        'account.account', string='CC Account Reference Name')

    # @api.model
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('payment_type'):
                if vals.get('payment_type') == 'outbound':
                    if vals.get('partner_type') and vals.get('partner_id'):
                        vals.update({'destination_account_id': self.env['res.partner'].search(
                            [('id', '=', vals.get('partner_id'))],
                            limit=1).property_account_payable_id.id})
                        vals['partner_type'] = 'supplier'
        res = super(AccountPayment, self).create(vals_list)
        self._cr.commit()
        return res

    @api.model
    def _prepare_payment_dict(self, payment):
        _logger.info('<--------- Customer Payment ----------> %s', payment)
        dup_val = {
            'amount': payment.get('TotalAmt'),
            'payment_date': payment.get('TxnDate'),
            'date': payment.get('TxnDate'),
            # 'payment_method_id': 1,
        }
        vals = {
            'qbo_payment_ref': payment.get('PaymentRefNum') if payment.get('PaymentRefNum') else False,
        }
        if 'CustomerRef' in payment:
            customer_id = self.env['res.partner'].get_parent_customer_ref(
                payment.get('CustomerRef').get('value'))
            vals.update({
                'qbo_payment_id': payment.get("Id"),
            })
            dup_val.update({
                'partner_type': 'customer',
                'partner_id': customer_id,
            })
            # vals.update({'destination_account_id': self.env['res.partner'].search([('id', '=', customer_id)], limit=1).property_account_receivable_id.id})
        if 'VendorRef' in payment:
            vendor_id = self.env['res.partner'].get_parent_vendor_ref(
                payment.get('VendorRef').get('value'))
            vals.update({
                'qbo_bill_payment_id': payment.get("Id"),
            })
            dup_val.update({
                'partner_type': 'supplier',
                'partner_id': vendor_id,

            })
            # vals.update({'destination_account_id': self.env['res.partner'].search([('id', '=', vendor_id)], limit=1).property_account_payable_id.id})

        # For payment
        if 'DepositToAccountRef' in payment:
            journal_id = self.env['account.journal'].get_journal_from_account(
                payment.get('DepositToAccountRef').get('value'))
            # vals.update({'journal_id': journal_id})
            dup_val.update({'journal_id': journal_id})

        # For Bill payment
        if 'APAccountRef' in payment:

            journal_id = self.env['account.journal'].get_journal_from_account(
                payment.get('APAccountRef').get('value'))
            # vals.update({'journal_id': journal_id})
            dup_val.update({'journal_id': journal_id})

        elif 'CheckPayment' in payment:
            if 'BankAccountRef' in payment.get('CheckPayment'):

                if 'value' in payment.get('CheckPayment').get('BankAccountRef'):
                    journal_id = self.env['account.journal'].get_journal_from_account(
                        payment.get('CheckPayment').get('BankAccountRef').get('value'))
                    # vals.update({'journal_id': journal_id})
                    dup_val.update({'journal_id': journal_id})

            else:
                _logger.info('CheckPayment does not contain BankAccountRef')

        elif 'CreditCardPayment' in payment:
            if 'CCAccountRef' in payment.get('CreditCardPayment'):

                if 'value' in payment.get('CreditCardPayment').get('CCAccountRef'):
                    journal_id = self.env['account.journal'].get_journal_from_account(
                        payment.get('CreditCardPayment').get('CCAccountRef').get('value'))
                    # vals.update({'journal_id': journal_id})
                    dup_val.update({'journal_id': journal_id})

            else:
                _logger.info('CreditCardPayment does not contain CCAccountRef')
        return vals, dup_val

    @api.model
    def create_transfer(self, data):

        """Import deposit from QBO
        :param data: deposit object response return by QBO
        :return account.payment: account deposit object
        """
        _logger.info(
            _('Inside Create deposit<------xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx0---->'))

        res = json.loads(str(data.text))

        if 'QueryResponse' in res:
            Payments = res.get('QueryResponse').get('Transfer', [])
        else:
            Payments = [res.get('Transfer')] or []

        _logger.info(
            _('Inside Create Transfer<------xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx111----> %s' % Payments))

        if len(Payments) == 0:
            raise UserError(
                "It seems that all of the Transfer are already imported.")
        last_imported_id = 0
        try:
            for payment in Payments:
                _logger.info(
                    _('Process for Transfer<------xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx111----> %s' % payment))

                dict_transfer = {}
                dict_transfer_line = {}
                dict_transfer_line2 = {}
                list_of_dict = []
                exist_deposit = self.env['account.move'].search([('qbo_transfer_id', '=', payment.get("Id"))],
                                                                limit=1)
                if not exist_deposit:
                    _logger.info(
                        _('Create for Transfer<------xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx111----> %s' % payment))
                    if payment.get('CurrencyRef').get('value'):
                        curr = payment.get(
                            'CurrencyRef').get('value')
                        currency = self.env['res.currency'].sudo().search(
                            [('active', 'in', [True, False]),
                             ('name', '=', curr)],
                            limit=1)
                        if currency and payment.get('ExchangeRate'):
                            rate_id = []
                            for rate in currency.rate_ids:
                                rate_id.append(str(rate.name))
                            if payment.get('TxnDate') in rate_id:
                                for rate in currency.rate_ids:
                                    if str(rate.name) == payment.get('TxnDate'):
                                        if not rate.inverse_company_rate == payment.get(
                                                'ExchangeRate'):
                                            rate.inverse_company_rate = payment.get(
                                                'ExchangeRate')
                            else:
                                self.env['res.currency.rate'].create({
                                    'name': payment.get('TxnDate'),
                                    'inverse_company_rate': payment.get('ExchangeRate'),
                                    'currency_id': currency.id,
                                    'company_id': self.env.company.id,
                                })
                            self._cr.commit()
                    if not currency.active:
                        currency.active = True
                    dict_transfer['move_type'] = 'entry'
                    dict_transfer['tax_state'] = 'notapplicable'
                    if payment.get('Id'):
                        dict_transfer['qbo_transfer_id'] = payment.get('Id')
                    if payment.get('TxnDate'):
                        dict_transfer['date'] = payment.get('TxnDate')
                    if self.env.company.transfer_journal_entry:
                        dict_transfer['journal_id'] = self.env.company.transfer_journal_entry.id
                    else:
                        raise ValidationError(
                            f"Set Transfer Journal On QB Account Configuration")

                    if payment.get("FromAccountRef").get("value") and payment.get("FromAccountRef"):
                        account_ref = self.env['account.account'].search(
                            [('qbo_id', '=', payment.get("FromAccountRef").get("value"))], limit=1)
                        if account_ref:
                            dict_transfer_line['account_id'] = account_ref.id
                            dict_transfer_line['currency_id'] = currency.id
                        else:
                            raise ValidationError(
                                f"Account Not Fond QBO Name[ID] {payment.get('FromAccountRef').get('name')}[{payment.get('FromAccountRef').get('value')}]--> Transfer Qbo Id {payment.get('Id')}")
                    if payment.get("Amount"):
                        converted_amount = currency._convert(abs(payment.get("Amount")), self.env.company.currency_id,
                                                             self.env.company, payment.get('TxnDate'))

                        dict_transfer_line['amount_currency'] = -payment.get("Amount")
                        dict_transfer_line['credit'] = converted_amount
                    if dict_transfer_line:
                        list_of_dict.append([0, 0, dict_transfer_line])

                    if payment.get("ToAccountRef").get("value") and payment.get("ToAccountRef"):
                        account_ref = self.env['account.account'].search(
                            [('qbo_id', '=', payment.get("ToAccountRef").get("value"))], limit=1)
                        if account_ref:
                            dict_transfer_line2['account_id'] = account_ref.id
                            dict_transfer_line2['currency_id'] = currency.id
                        else:
                            raise ValidationError(
                                f"Account Not Found QBO Name[ID] {payment.get('ToAccountRef').get('name')}[{payment.get('ToAccountRef').get('value')}] --> Transfer Qbo Id {payment.get('Id')}")
                    if payment.get("Amount"):
                        converted_amount = currency._convert(abs(payment.get("Amount")), self.env.company.currency_id,
                                                             self.env.company, payment.get('TxnDate'))
                        dict_transfer_line2['amount_currency'] = payment.get("Amount")
                        dict_transfer_line2['debit'] = converted_amount
                    if dict_transfer_line:
                        list_of_dict.append([0, 0, dict_transfer_line2])
                    dict_transfer['invoice_line_ids'] = list_of_dict
                    transfer_entry = self.env['account.move'].create(dict_transfer)
                    transfer_entry.action_post()
                    self._cr.commit()
                    _logger.info(
                        _('Create Transfer Line<------xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx111----> %s' % transfer_entry.id))
                    last_imported_id = payment.get('Id')
                else:
                    _logger.info(
                        _('Transfer Already Imported QBO ID is %s' % payment.get("Id")))


        except Exception as e:
            raise ValidationError(_('Error : %s' % e))
        return last_imported_id

    @api.model
    def create_deposit(self, data):
        """Import deposit from QBO
        :param data: deposit object response return by QBO
        :return account.payment: account deposit object
        """
        _logger.info(
            _('Inside Create deposit<------xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx0---->'))
        res = json.loads(str(data.text))
        if 'QueryResponse' in res:
            Payments = res.get('QueryResponse').get('Deposit', [])
        else:
            Payments = [res.get('Deposit')] or []
        _logger.info(
            _('Inside Create Deposit<------xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx111----> %s' % Payments))
        if len(Payments) == 0:
            raise UserError(
                "It seems that all of the Deposit are already imported.")
        last_imported_id = 0
        try:
            dict_deposit = {}
            for payment in Payments:
                _logger.info(f"Process Deposit is================ {payment}.")
                if payment.get('Line'):
                    if not payment.get('Line')[0].get('DetailType') == 'DepositLineDetail':
                        last_imported_id = payment.get('Id')
                    else:
                        exist_deposit = self.env['account.move'].search([('qbo_deposit_id', '=', payment.get("Id"))],
                                                                        limit=1)

                        if payment.get('CurrencyRef').get('value'):
                            curr = payment.get(
                                'CurrencyRef').get('value')
                            currency = self.env['res.currency'].sudo().search(
                                [('active', 'in', [True, False]),
                                 ('name', '=', curr)],
                                limit=1)
                            if currency and payment.get('ExchangeRate'):
                                rate_id = []
                                for rate in currency.rate_ids:
                                    rate_id.append(str(rate.name))
                                if payment.get('TxnDate') in rate_id:
                                    for rate in currency.rate_ids:
                                        if str(rate.name) == payment.get('TxnDate'):
                                            if not rate.inverse_company_rate == payment.get(
                                                    'ExchangeRate'):
                                                rate.inverse_company_rate = payment.get(
                                                    'ExchangeRate')
                                else:
                                    self.env['res.currency.rate'].create({
                                        'name': payment.get('TxnDate'),
                                        'inverse_company_rate': payment.get('ExchangeRate'),
                                        'currency_id': currency.id,
                                        'company_id': self.env.company.id,
                                    })
                                self._cr.commit()
                        if not currency.active:
                            currency.active = True
                        if not exist_deposit:
                            dict_deposit['move_type'] = 'entry'
                            if payment.get('GlobalTaxCalculation'):
                                if payment.get('GlobalTaxCalculation') == 'TaxExcluded':
                                    dict_deposit['tax_state'] = 'exclusive'
                                elif payment.get('GlobalTaxCalculation') == 'TaxInclusive':
                                    dict_deposit['tax_state'] = 'inclusive'
                                elif payment.get('GlobalTaxCalculation') == 'NotApplicable':
                                    dict_deposit['tax_state'] = 'notapplicable'
                            if payment.get('Id'):
                                dict_deposit['qbo_deposit_id'] = payment.get('Id')
                            if payment.get('TxnDate'):
                                dict_deposit['date'] = payment.get('TxnDate')
                            if self.env.company.deposit_journal_entry:
                                dict_deposit['journal_id'] = self.env.company.deposit_journal_entry.id
                            else:
                                raise ValidationError(
                                    f"Set Deposit Journal On QB Account Configuration")
                            line_list = []
                            if payment.get("Line"):
                                for line in payment.get("Line"):
                                    dict_deposit_line = {}
                                    # dict_deposit_line['move_id'] = deposit_entry.id
                                    if line.get("DepositLineDetail") and line.get("DepositLineDetail").get(
                                            "AccountRef"):
                                        account_ref = self.env['account.account'].search(
                                            [('qbo_id', '=',
                                              line.get("DepositLineDetail").get("AccountRef").get('value'))],
                                            limit=1)
                                        if account_ref:
                                            dict_deposit_line['account_id'] = account_ref.id
                                        else:
                                            raise ValidationError(
                                                f"Account Not Found QBO ID {line.get('DepositLineDetail').get('AccountRef').get('value')}/{line.get('DepositLineDetail').get('AccountRef').get('name')} Deposit Id{payment.get('Id')}")
                                    if line.get("DepositLineDetail") and line.get("DepositLineDetail").get(
                                            "Entity") and line.get("DepositLineDetail").get("Entity").get("value"):
                                        if line.get("DepositLineDetail").get("Entity").get("type") == 'EMPLOYEE':
                                            employee_ref = self.env['hr.employee'].search(
                                                [
                                                    ('quickbook_id', '=',
                                                     line.get("DepositLineDetail").get("Entity").get("value")),
                                                ],
                                                limit=1)
                                            if employee_ref.related_contact_ids:
                                                partner_ref = employee_ref.related_contact_ids[0]
                                            else:
                                                partner_ref = False
                                        else:
                                            partner_ref = self.env['res.partner'].search(
                                                ['|',
                                                 ('qbo_customer_id', '=',
                                                  line.get("DepositLineDetail").get("Entity").get("value")),
                                                 ('qbo_vendor_id', '=',
                                                  line.get("DepositLineDetail").get("Entity").get("value"))],
                                                limit=1)
                                        if partner_ref:
                                            dict_deposit_line['partner_id'] = partner_ref.id
                                        else:
                                            raise ValidationError(
                                                f"Partner or Employee Not Found QBO ID {payment.get('Id')}")
                                    if line.get("DepositLineDetail").get("CheckNum"):
                                        dict_deposit_line['name'] = line.get("DepositLineDetail").get("CheckNum")
                                    if line.get("Amount"):
                                        dict_deposit_line['credit'] = line.get("Amount")
                                        dict_deposit_line['currency_id'] = currency.id
                                    if line.get("DepositLineDetail").get("TaxCodeRef") and line.get(
                                            "DepositLineDetail").get("TaxCodeRef").get("value") != 'NON':
                                        tax = self.env['account.tax'].search([('qbo_tax_id', '=',
                                                                               line.get("DepositLineDetail").get(
                                                                                   "TaxCodeRef").get("value"))],
                                                                             limit=1)
                                        if tax:
                                            dict_deposit_line['tax_ids'] = [[6, False, [tax.id]]]

                                    list_of_dict = [0, 0, dict_deposit_line]
                                    line_list.append(list_of_dict)
                                if payment.get('DepositToAccountRef') and payment.get('DepositToAccountRef').get(
                                        'value'):
                                    account_ref = self.env['account.account'].search(
                                        [('qbo_id', '=', payment.get("DepositToAccountRef").get('value'))],
                                        limit=1)
                                    if account_ref:
                                        account_id = account_ref.id
                                    else:
                                        raise ValidationError(
                                            f"Account Not Find QBO ID {line.get('AccountRef').get('value')}")
                                if payment.get('TotalAmt'):
                                    debit = payment.get('TotalAmt')
                                line_list.append([0, 0, {
                                    'account_id': account_id,
                                    'debit': debit,
                                    'currency_id': currency.id
                                }])
                                dict_deposit['invoice_line_ids'] = line_list
                                deposit_entry = self.env['account.move'].create(dict_deposit)
                                deposit_entry.action_post()
                                self._cr.commit()
                                _logger.info(
                                    _('Create Deposit Line<------xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx111----> %s' % deposit_entry.id))
                        last_imported_id = payment.get('Id')
                        self._cr.commit()
        except Exception as e:
            raise ValidationError(_('Error : %s' % e))
        return last_imported_id

    @api.model
    def create_expenses(self, data):
        """Import deposit from QBO
        :param data: deposit object response return by QBO
        :return account.payment: account deposit object
        """
        _logger.info(
            _('Inside Create deposit<------xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx0---->'))

        res = json.loads(str(data.text))

        if 'QueryResponse' in res:
            Payments = res.get('QueryResponse').get('Purchase', [])
        else:
            Payments = [res.get('Purchase')] or []

        _logger.info(
            _('Inside Create Deposit<------xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx111----> %s' % Payments))

        if len(Payments) == 0:
            raise UserError(
                "It seems that all of the Expenses are already imported.")
        last_imported_id = 0
        try:
            dict_deposit = {}
            for payment in Payments:
                exist_deposit = self.env['account.move'].search([('qbo_expns_id', '=', payment.get("Id"))],
                                                                limit=1)
                if not exist_deposit:
                    if payment.get('CurrencyRef').get('value'):
                        curr = payment.get(
                            'CurrencyRef').get('value')
                        currency = self.env['res.currency'].sudo().search(
                            [('active', 'in', [True, False]),
                             ('name', '=', curr)],
                            limit=1)
                        if currency and payment.get('ExchangeRate'):
                            rate_id = []
                            for rate in currency.rate_ids:
                                rate_id.append(str(rate.name))
                            if payment.get('TxnDate') in rate_id:
                                for rate in currency.rate_ids:
                                    if str(rate.name) == payment.get('TxnDate'):
                                        if not rate.inverse_company_rate == payment.get(
                                                'ExchangeRate'):
                                            rate.inverse_company_rate = payment.get(
                                                'ExchangeRate')
                            else:
                                self.env['res.currency.rate'].create({
                                    'name': payment.get('TxnDate'),
                                    'inverse_company_rate': payment.get('ExchangeRate'),
                                    'currency_id': currency.id,
                                    'company_id': self.env.company.id,
                                })
                            self._cr.commit()
                    currency_state = True
                    if not currency.active:
                        currency.active = True
                    if self.env.company.currency_id != currency.id:
                        currency_state = False
                    dict_deposit['move_type'] = 'entry'
                    if payment.get('GlobalTaxCalculation'):
                        if payment.get('GlobalTaxCalculation') == 'TaxExcluded':
                            dict_deposit['tax_state'] = 'exclusive'
                        elif payment.get('GlobalTaxCalculation') == 'TaxInclusive':
                            dict_deposit['tax_state'] = 'inclusive'
                        elif payment.get('GlobalTaxCalculation') == 'NotApplicable':
                            dict_deposit['tax_state'] = 'notapplicable'

                    if payment.get('Id'):
                        dict_deposit['qbo_expns_id'] = payment.get('Id')
                    if payment.get('TxnDate'):
                        dict_deposit['date'] = payment.get('TxnDate')
                    if self.env.company.expense_journal_entry:
                        dict_deposit['journal_id'] = self.env.company.expense_journal_entry.id
                    else:
                        raise ValidationError(
                            f"Set Expenses Journal On QB Account Configuration")
                    line_list = []
                    if payment.get("Line"):
                        for line in payment.get("Line"):
                            dict_deposit_line = {}
                            if line.get("ItemBasedExpenseLineDetail"):
                                if line.get("ItemBasedExpenseLineDetail").get("ItemRef").get("value") and line.get(
                                        "ItemBasedExpenseLineDetail").get("ItemRef"):
                                    prod = self.env['product.product'].search([("qbo_product_id", '=',
                                                                                line.get(
                                                                                    "ItemBasedExpenseLineDetail").get(
                                                                                    "ItemRef").get("value"))], limit=1)
                                    if not prod:
                                        raise ValidationError(
                                            f'Product Not Find QBO ID {line.get("ItemBasedExpenseLineDetail").get("ItemRef").get("value")}')
                                    else:
                                        if prod.property_account_expense_id:
                                            dict_deposit_line['account_id'] = prod.property_account_expense_id.id
                                        elif prod.categ_id.property_account_expense_categ_id:
                                            dict_deposit_line['account_id'] = prod.property_account_expense_id.id
                                        else:
                                            raise ValidationError(
                                                f'Expense account Not set for product QBO ID {line.get("ItemBasedExpenseLineDetail").get("ItemRef").get("value")}')
                                if line.get("Amount"):
                                    dict_deposit_line['debit'] = line.get("Amount")
                                    amount = line.get("Amount")
                                    dict_deposit_line['currency_id'] = currency.id

                                if line.get("ItemBasedExpenseLineDetail").get("TaxCodeRef") and line.get(
                                        "ItemBasedExpenseLineDetail").get("TaxCodeRef").get("value") != 'NON':
                                    tax = self.env['account.tax'].search([('qbo_tax_id', '=',
                                                                           line.get("ItemBasedExpenseLineDetail").get(
                                                                               "TaxCodeRef").get("value"))], limit=1)
                                    if tax:
                                        dict_deposit_line['tax_ids'] = [[6, False, [tax.id]]]
                                    else:
                                        raise ValidationError(
                                            f'Tax not Found QBO ID {line.get("ItemBasedExpenseLineDetail").get("TaxCodeRef").get("value")}')

                            elif line.get("AccountBasedExpenseLineDetail"):
                                if line.get("AccountBasedExpenseLineDetail").get("AccountRef").get(
                                        "value") and line.get(
                                    "AccountBasedExpenseLineDetail").get("AccountRef"):
                                    res_account = self.env['account.account'].search(
                                        [('qbo_id', '=',
                                          line.get("AccountBasedExpenseLineDetail").get("AccountRef").get("value"))],
                                        limit=1)
                                    if res_account:
                                        dict_deposit_line['account_id'] = res_account.id
                                    else:
                                        raise ValidationError(
                                            f'Expense account Not Found QBO ID {line.get("AccountBasedExpenseLineDetail").get("ItemRef").get("value")}')
                                if line.get("Amount"):
                                    dict_deposit_line['debit'] = line.get("Amount")
                                    amount = line.get("Amount")
                                    dict_deposit_line['currency_id'] = currency.id

                                if line.get("AccountBasedExpenseLineDetail").get("TaxCodeRef") and line.get(
                                        "AccountBasedExpenseLineDetail").get("TaxCodeRef").get("value") != 'NON':
                                    tax = self.env['account.tax'].search([('qbo_tax_id', '=',
                                                                           line.get(
                                                                               "AccountBasedExpenseLineDetail").get(
                                                                               "TaxCodeRef").get("value"))], limit=1)
                                    if tax:
                                        dict_deposit_line['tax_ids'] = [[6, False, [tax.id]]]
                                    else:
                                        raise ValidationError(
                                            f'Tax not Found QBO ID {line.get("AccountBasedExpenseLineDetail").get("TaxCodeRef").get("value")}')

                            if line.get("Description"):
                                dict_deposit_line['name'] = line.get("Description")
                            if not currency_state:
                                converted_amount = currency._convert(abs(amount), self.env.company.currency_id,
                                                                     self.env.company, payment.get('TxnDate'))
                                dict_deposit_line['amount_currency'] = amount
                                dict_deposit_line['debit'] = converted_amount

                            list_of_dict = [0, 0, dict_deposit_line]
                            line_list.append(list_of_dict)
                        if payment.get('TotalAmt'):
                            credit = payment.get('TotalAmt')
                        account_id = self.env['account.account'].search(
                            [('qbo_id', '=', payment.get('AccountRef').get('value'))], limit=1)
                        if not currency_state:
                            converted_amount = currency._convert(abs(credit), self.env.company.currency_id,
                                                                 self.env.company, payment.get('TxnDate'))
                            amount_currency = converted_amount
                        line_list.append([0, 0, {
                            'account_id': account_id.id,
                            'credit': amount_currency,
                            'currency_id': currency.id,
                            'amount_currency': -credit
                        }])

                        dict_deposit['invoice_line_ids'] = line_list
                        dict_deposit.update({'currency_id': currency.id})
                        # self._context['type'] = 'exp'

                        deposit_entry = self.env['account.move'].create(dict_deposit)
                        deposit_entry.action_post()
                        self._cr.commit()
                        _logger.info(
                            _('Create Deposit Line<------xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx111----> %s' % deposit_entry.id))
                last_imported_id = payment.get('Id')
        except Exception as e:
            raise ValidationError(_('Error : %s' % e))
        return last_imported_id

    @api.model
    def create_payment(self, data, is_customer=False, is_vendor=False):
        """Import payment from QBO
        :param data: payment object response return by QBO
        :return account.payment: account payment object
        """
        _logger.info(
            _('Inside Create Payment<------xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx0---->'))

        company = self.env['res.company'].search([('id', '=', 1)], limit=1)

        res = json.loads(str(data.text))

        if is_customer:
            if 'QueryResponse' in res:
                Payments = res.get('QueryResponse').get('Payment', [])
            else:
                Payments = [res.get('Payment')] or []
        elif is_vendor:

            if 'QueryResponse' in res:
                Payments = res.get('QueryResponse').get('BillPayment', [])
            else:
                Payments = [res.get('BillPayment')] or []

        _logger.info(
            _('Inside Create Payment<------xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx111----> %s' % Payments))

        if len(Payments) == 0:
            raise UserError(
                "It seems that all of the Customers/Vendors Payments are already imported.")
        last_imported_id = 0
        try:
            payment_obj = False
            count = 0
            for payment in Payments:
                last_imported_id = payment.get('Id')
                payment_obj = False
                count = count + 1
                _logger.info(_('\n\nPayment1 : %s %s' % (count, payment)))
                if 'TotalAmt' in payment and payment.get('TotalAmt'):
                    invoice = False
                    payment_obj_rec = False
                    if payment is None:
                        payment = False
                    # if len(payment.get('Line')) > 0:
                    #     if payment and 'LinkedTxn' in payment.get('Line')[0]:
                    #         txn = payment.get('Line')[0].get('LinkedTxn')
                    #         if txn and (txn[0].get('TxnType') == 'Invoice' or txn[0].get('TxnType') == 'Bill'):
                    #             qbo_inv_ref = txn[0].get('TxnId')
                    #             invoice = self.env['account.move'].search([('qbo_invoice_id', '=', qbo_inv_ref)], limit=1)
                    if len(payment.get('Line')) > 0:
                        i = 0
                        payment_obj_rec = self.search(
                            [('qbo_bill_payment_id', '=', payment.get("Id"))])
                        if not payment_obj_rec:
                            payment_obj_rec = self.search(
                                [('qbo_payment_id', '=', payment.get("Id"))])

                        if not payment_obj_rec:
                            for inv_rec in payment.get('Line'):
                                i = i + 1
                                invoice = False

                                if 'LinkedTxn' in inv_rec and inv_rec.get('LinkedTxn'):
                                    if inv_rec.get('LinkedTxn') and (
                                            inv_rec.get('LinkedTxn')[0].get('TxnType') == 'Invoice' or
                                            inv_rec.get('LinkedTxn')[0].get('TxnType') == 'Bill'):

                                        if inv_rec.get('LinkedTxn')[0].get('TxnId'):
                                            invoice = self.env['account.move'].search(
                                                [('qbo_invoice_id', '=', inv_rec.get(
                                                    'LinkedTxn')[0].get('TxnId'))],
                                                limit=1)

                                        if not invoice:
                                            vals, dup_val = self._prepare_payment_dict(
                                                payment)
                                            _logger.info(
                                                '<------xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx1----> ')

                                            if dup_val == 0:
                                                _logger.info(
                                                    '<---------Payment Amount is Zero----------> ')
                                                continue

                                            if 'journal_id' not in dup_val:
                                                raise ValidationError(
                                                    _('Payment Journal required'))
                                                # create payment
                                                # payment_obj = self.create(vals)
                                                # payment_obj.action_post()
                                            del dup_val['payment_date']
                                            dup_val.update(
                                                {'amount': inv_rec.get('Amount')})
                                            if is_customer:
                                                dup_val.update(
                                                    {'partner_type': 'customer'})
                                                dup_val.update(
                                                    {'payment_type': 'inbound'})

                                            elif is_vendor:
                                                dup_val.update(
                                                    {'payment_type': 'outbound'})
                                                dup_val.update(
                                                    {'partner_type': 'supplier'})
                                            payment_obj = self.env[
                                                'account.payment'].create(dup_val)
                                            payment_obj.action_post()
                                            payment_obj.sudo().write(vals)
                                            # payment_obj._cr.commit()
                                            if payment_obj:
                                                if is_customer:
                                                    company.sudo().write(
                                                        {'last_imported_payment_id': payment_obj.qbo_payment_id})
                                                    # company._cr.commit()

                                                elif is_vendor:
                                                    date_object = None
                                                    if company.import_vp_by_date:
                                                        date_format = '%Y-%m-%d'
                                                        if company.vendor_paymnt_import_by == 'crt_dt':
                                                            date_string = payment.get('MetaData').get(
                                                                'CreateTime')[:10]
                                                        elif company.vendor_paymnt_import_by == 'updt_dt':
                                                            date_string = payment.get('MetaData').get(
                                                                'LastUpdatedTime')[:10]
                                                        else:
                                                            date_string = payment.get('TxnDate')

                                                        date_object = datetime.strptime(date_string,
                                                                                        date_format).date()
                                                        # company.import_vp_date = date_object
                                                    company.sudo().write({
                                                        'last_imported_bill_payment_id': payment_obj.qbo_bill_payment_id,
                                                        'import_vp_date': date_object if date_object else None})
                                                    # company._cr.commit()

                                            _logger.info(
                                                _("Payment created sucessfully! Payment Id: %s" % (payment_obj.id)))
                                            company = self.env.user.company_id
                                            if is_customer:
                                                if company.import_cp_by_date:
                                                    date_format = '%Y-%m-%d'
                                                    if company.customer_paymnt_import_by == 'crt_dt':
                                                        date_string = payment.get('MetaData').get(
                                                            'CreateTime')[:10]
                                                    elif company.customer_paymnt_import_by == 'updt_dt':
                                                        date_string = payment.get('MetaData').get(
                                                            'LastUpdatedTime')[:10]
                                                    else:
                                                        date_string = payment.get('TxnDate')

                                                    date_object = datetime.strptime(date_string,
                                                                                    date_format).date()
                                                    company.import_cp_date = date_object
                                                elif is_vendor:
                                                    if company.import_vp_by_date:
                                                        date_format = '%Y-%m-%d'
                                                        if company.vendor_paymnt_import_by == 'crt_dt':
                                                            date_string = payment.get('MetaData').get(
                                                                'CreateTime')[:10]
                                                        elif company.vendor_paymnt_import_by == 'updt_dt':
                                                            date_string = payment.get('MetaData').get(
                                                                'LastUpdatedTime')[:10]
                                                        else:
                                                            date_string = payment.get('TxnDate')

                                                        date_object = datetime.strptime(date_string,
                                                                                        date_format).date()
                                                        company.import_vp_date = date_object
                                                self._cr.commit()

                                            # _logger.info('Vendor Bill/Invoice does not exists for this payment \n%s', payment)
                                            # continue
                                            #
                                        else:
                                            vals, dup_val = self._prepare_payment_dict(
                                                payment)
                                            if dup_val == 0:
                                                _logger.info(
                                                    '<---------Payment Amount is Zero----------> ')
                                                continue
                                            if invoice.state == 'draft':
                                                _logger.info('<---------Invoice is going to open state----------> %s',
                                                             invoice)
                                                if invoice.invoice_line_ids:
                                                    invoice.action_post()
                                            dup_val.update(
                                                {'amount': inv_rec.get('Amount')})
                                            vals.update({'ref': invoice.name})
                                            # vals.update({'reconciled_invoice_ids': [(4, invoice.id, None)]})

                                            if 'journal_id' not in dup_val:
                                                get_payments = self.env[
                                                    'account.payment'].search([])
                                                for pay in get_payments:
                                                    if pay.invoice_ids:
                                                        for inv in pay.invoice_ids:
                                                            if inv.id == invoice.id:
                                                                if pay.journal_id:
                                                                    dup_val.update(
                                                                        {'journal_id': pay.journal_id.id})

                                            # if invoice.partner_id.customer_rank:
                                            #     dup_val.update({'payment_type': 'inbound'})
                                            # elif invoice.partner_id.supplier_rank:
                                            #     dup_val.update({'payment_type': 'outbound'})

                                            if 'journal_id' not in dup_val:
                                                raise ValidationError(
                                                    _('Payment Journal required'))
                                                # create payment
                                            # payment_obj = self.create(vals)
                                            # payment_obj.action_post()

                                            if not invoice.amount_residual <= 0:
                                                if is_customer:
                                                    dup_val.update(
                                                        {'partner_type': 'customer'})
                                                    dup_val.update(
                                                        {'payment_type': 'inbound'})

                                                elif is_vendor:
                                                    dup_val.update(
                                                        {'payment_type': 'outbound'})
                                                    dup_val.update(
                                                        {'partner_type': 'supplier'})

                                                del dup_val['date']
                                                register_payments = self.env['account.payment.register'].with_context(
                                                    active_model='account.move',
                                                    active_ids=invoice.id).create(dup_val)

                                                invoice = False
                                                _logger.info(
                                                    '___________________create PAyment Method')
                                                payment_obj = register_payments._create_payments()

                                                payment_obj.sudo().write(vals)
                                                # payment_obj._cr.commit()
                                                if payment_obj:

                                                    if is_customer:
                                                        if payment_obj.qbo_payment_id:
                                                            company.sudo().write(
                                                                {
                                                                    'last_imported_payment_id': payment_obj.qbo_payment_id})
                                                            # company._cr.commit()

                                                    elif is_vendor:
                                                        if payment_obj.qbo_payment_id:
                                                            company.sudo().write({
                                                                'last_imported_bill_payment_id': payment_obj.qbo_bill_payment_id})
                                                            # company._cr.commit()

                                                _logger.info(
                                                    _("Payment created sucessfully! Payment Id: %s" % (payment_obj.id)))
                                                company = self.env.user.company_id
                                                if is_customer:
                                                    if company.import_cp_by_date:
                                                        date_format = '%Y-%m-%d'
                                                        if company.customer_paymnt_import_by == 'crt_dt':
                                                            date_string = payment.get('MetaData').get(
                                                                'CreateTime')[:10]
                                                        elif company.customer_paymnt_import_by == 'updt_dt':
                                                            date_string = payment.get('MetaData').get(
                                                                'LastUpdatedTime')[:10]
                                                        else:
                                                            date_string = payment.get('TxnDate')

                                                        date_object = datetime.strptime(date_string,
                                                                                        date_format).date()
                                                        company.import_cp_date = date_object
                                                    elif is_vendor:
                                                        if company.import_vp_by_date:
                                                            date_format = '%Y-%m-%d'
                                                            if company.vendor_paymnt_import_by == 'crt_dt':
                                                                date_string = payment.get('MetaData').get(
                                                                    'CreateTime')[:10]
                                                            elif company.vendor_paymnt_import_by == 'updt_dt':
                                                                date_string = payment.get('MetaData').get(
                                                                    'LastUpdatedTime')[:10]
                                                            else:
                                                                date_string = payment.get('TxnDate')

                                                            date_object = datetime.strptime(date_string,
                                                                                            date_format).date()
                                                            company.import_vp_date = date_object

                                                    if payment.get('CurrencyRef').get('value'):
                                                        curr = payment.get(
                                                            'CurrencyRef').get('value')
                                                        currency = self.env['res.currency'].sudo().search(
                                                            [('active', 'in', [True, False]),
                                                             ('name', '=', curr)],
                                                            limit=1)
                                                        if currency and payment.get('ExchangeRate'):
                                                            rate_id = []
                                                            for rate in currency.rate_ids:
                                                                rate_id.append(str(rate.name))
                                                            if payment.get('TxnDate') in rate_id:
                                                                for rate in currency.rate_ids:
                                                                    if str(rate.name) == payment.get('TxnDate'):
                                                                        if not rate.inverse_company_rate == payment.get(
                                                                                'ExchangeRate'):
                                                                            rate.inverse_company_rate = payment.get(
                                                                                'ExchangeRate')
                                                            else:
                                                                self.env['res.currency.rate'].create({
                                                                    'name': payment.get('TxnDate'),
                                                                    'inverse_company_rate': payment.get('ExchangeRate'),
                                                                    'currency_id': currency.id,
                                                                    'company_id': self.env.company.id,
                                                                })
                                                            self._cr.commit()
                                                    dup_val.update({'currency_id': currency.id})

                                            else:

                                                del dup_val['payment_date']
                                                if is_customer:
                                                    dup_val.update(
                                                        {'partner_type': 'customer'})
                                                    dup_val.update(
                                                        {'payment_type': 'inbound'})

                                                elif is_vendor:
                                                    dup_val.update(
                                                        {'payment_type': 'outbound'})
                                                    dup_val.update(
                                                        {'partner_type': 'supplier'})
                                                if payment.get('CurrencyRef').get('value'):
                                                    curr = payment.get(
                                                        'CurrencyRef').get('value')
                                                    currency = self.env['res.currency'].sudo().search(
                                                        [('active', 'in', [True, False]),
                                                         ('name', '=', curr)],
                                                        limit=1)
                                                    if not currency.active:
                                                        currency.active = True
                                                        self._cr.commit()
                                                    if currency and payment.get('ExchangeRate'):
                                                        rate_id = []
                                                        for rate in currency.rate_ids:
                                                            rate_id.append(str(rate.name))
                                                        if payment.get('TxnDate') in rate_id:
                                                            for rate in currency.rate_ids:
                                                                if str(rate.name) == payment.get('TxnDate'):
                                                                    if not rate.inverse_company_rate == payment.get(
                                                                            'ExchangeRate'):
                                                                        rate.inverse_company_rate = payment.get(
                                                                            'ExchangeRate')
                                                        else:
                                                            self.env['res.currency.rate'].create({
                                                                'name': payment.get('TxnDate'),
                                                                'inverse_company_rate': payment.get('ExchangeRate'),
                                                                'currency_id': currency.id,
                                                                'company_id': self.env.company.id,
                                                            })
                                                        self._cr.commit()
                                                dup_val.update({'currency_id': currency.id})
                                                payment_obj_rec = self.search(
                                                    [('qbo_bill_payment_id', '=', payment.get("Id"))])
                                                for rec in payment_obj_rec:
                                                    rec.unlink()

                                                payment_obj = self.env[
                                                    'account.payment'].create(dup_val)
                                                payment_obj.action_post()
                                                payment_obj.sudo().write(vals)
                                                # payment_obj._cr.commit()
                                                if payment_obj:
                                                    if is_customer:
                                                        if payment_obj.qbo_payment_id:
                                                            if payment_obj.qbo_payment_id:
                                                                company.sudo().write({
                                                                    'last_imported_payment_id': payment_obj.qbo_payment_id})
                                                                # company._cr.commit()

                                                    elif is_vendor:
                                                        if payment_obj.qbo_payment_id:
                                                            if payment_obj.qbo_payment_id:
                                                                company.sudo().write({
                                                                    'last_imported_bill_payment_id': payment_obj.qbo_bill_payment_id, })
                                                                # company._cr.commit()

                                                _logger.info(
                                                    _("Payment created sucessfully1! Payment Id: %s" % (
                                                        payment_obj.id)))

                    # if not invoice and not payment_obj:
                    #     vals, dup_val = self._prepare_payment_dict(payment)
                    #     _logger.info(
                    #         _('<------xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx2----> %s %s' % (vals, dup_val)))
                    #
                    #     if dup_val == 0:
                    #         _logger.info(
                    #             '<---------Payment Amount is Zero----------> ')
                    #
                    #     _logger.info(
                    #         _('<------xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx3----> '))
                    #     payment_obj = self.search(
                    #         [('qbo_bill_payment_id', '=', payment.get("Id"))], limit=1)
                    #     _logger.info(
                    #         _('<------xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx4----> %s' % payment_obj))
                    #
                    #     if not payment_obj:
                    #         if 'journal_id' not in dup_val:
                    #             raise ValidationError(
                    #                 _('Payment Journal required'))
                    #             # create payment
                    #         # payment_obj = self.create(vals)
                    #         # payment_obj.action_post()
                    #     del dup_val['payment_date']
                    #     if is_customer:
                    #         dup_val.update({'partner_type': 'customer'})
                    #         dup_val.update({'payment_type': 'inbound'})
                    #
                    #     elif is_vendor:
                    #         dup_val.update({'payment_type': 'outbound'})
                    #         dup_val.update({'partner_type': 'supplier'})
                    #     payment_obj = self.env[
                    #         'account.payment'].create(dup_val)
                    #     payment_obj.action_post()
                    #     payment_obj.sudo().write(vals)
                    #     # payment_obj._cr.commit()
                    #     if payment_obj:
                    #         if is_customer:
                    #             if payment_obj.qbo_payment_id:
                    #                 if payment_obj.qbo_payment_id:
                    #                     company.sudo().write(
                    #                         {'last_imported_payment_id': payment_obj.qbo_payment_id})
                    #                     # company._cr.commit()
                    #
                    #         elif is_vendor:
                    #             if payment_obj.qbo_payment_id:
                    #                 if payment_obj.qbo_payment_id:
                    #                     company.sudo().write(
                    #                         {'last_imported_bill_payment_id': payment_obj.qbo_bill_payment_id})
                    #                     # company._cr.commit()
                    #
                    #     _logger.info(
                    #         _("Payment created sucessfully22! Payment Id: %s" % (payment_obj.id)))
                    #     company = self.env['res.company']
                    #     if company.import_vp_by_date:
                    #         date_format = '%Y-%m-%d'
                    #         if company.vendor_paymnt_import_by == 'crt_dt':
                    #             date_string = payment.get('MetaData').get(
                    #                 'CreateTime')[:10]
                    #         elif company.vendor_paymnt_import_by == 'updt_dt':
                    #             date_string = payment.get('MetaData').get(
                    #                 'LastUpdatedTime')[:10]
                    #         else:
                    #             date_string = payment.get('TxnDate')
                    #
                    #         date_object = datetime.strptime(date_string,
                    #                                         date_format).date()
                    #         company.import_vp_date = date_object
                    #         self._cr.commit()

                _logger.info(
                    _('\n\nEnd of For : %s %s' % (count, payment_obj)))
        except Exception as e:
            raise ValidationError(_('Error : %s' % e))

        _logger.info(
            _('\n\nLast Payment Object: %s %s' % (count, payment_obj)))
        return last_imported_id

    # @api.model
    # def create_payment(self, data, is_customer=False, is_vendor=False):
    #     """Import payment from QBO
    #     :param data: payment object response return by QBO
    #     :return account.payment: account payment object
    #     """
    #     company = self.env['res.company'].search([('id', '=', 1)], limit=1)
    #
    #     res = json.loads(str(data.text))
    #
    #
    #     if is_customer:
    #         if 'QueryResponse' in res:
    #             Payments = res.get('QueryResponse').get('Payment', [])
    #         else:
    #             Payments = [res.get('Payment')] or []
    #     elif is_vendor:
    #
    #         if 'QueryResponse' in res:
    #             Payments = res.get('QueryResponse').get('BillPayment', [])
    #         else:
    #             Payments = [res.get('BillPayment')] or []
    #
    #     payment_obj = False
    #     count = 0
    #     for payment in Payments:
    #         if payment.get('TotalAmt'):
    #             invoice = False
    #             if payment is None:
    #                 payment = False
    #             if len(payment.get('Line')) > 0:
    #                 if payment and 'LinkedTxn' in payment.get('Line')[0]:
    #                     txn = payment.get('Line')[0].get('LinkedTxn')
    #                     if txn and (txn[0].get('TxnType') == 'Invoice' or txn[0].get('TxnType') == 'Bill'):
    #                         qbo_inv_ref = txn[0].get('TxnId')
    #                         invoice = self.env['account.move'].search([('qbo_invoice_id', '=', qbo_inv_ref)], limit=1)
    #
    #             if not invoice:
    #
    #                 vals, dup_val = self._prepare_payment_dict(payment)
    #                 _logger.info('<------xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx----> ')
    #
    #                 if dup_val == 0:
    #                     _logger.info('<---------Payment Amount is Zero----------> ')
    #                     continue
    #
    #
    #                 payment_obj = self.search([('qbo_bill_payment_id', '=', payment.get("Id"))], limit=1)
    #
    #                 if not payment_obj:
    #                     if 'journal_id' not in dup_val:
    #                         raise ValidationError(_('Payment Journal required'))
    # create payment
    # payment_obj = self.create(vals)
    # payment_obj.action_post()
    #                 del dup_val['payment_date']
    #                 if is_customer:
    #                     dup_val.update({'payment_type': 'inbound'})
    #
    #                 elif is_vendor:
    #                     dup_val.update({'payment_type': 'outbound'})
    #
    #                 payment_obj = self.env['account.payment'].create(dup_val)
    #                 payment_obj.action_post()
    #
    #                 payment_obj.sudo().write(vals)
    #
    #                 payment_obj._cr.commit()
    #                 if payment_obj:
    #                     if is_customer:
    #                         company.sudo().write({'last_imported_payment_id': payment_obj.qbo_payment_id})
    #                         company._cr.commit()
    #
    #                     elif is_vendor:
    #                         company.sudo().write({'last_imported_bill_payment_id': payment_obj.qbo_bill_payment_id})
    #                         company._cr.commit()
    #
    #                 _logger.info(_("Payment created sucessfully! Payment Id: %s" % (payment_obj.id)))
    #
    # _logger.info('Vendor Bill/Invoice does not exists for this payment \n%s', payment)
    # continue
    #                 #
    #             else:
    #                 vals,dup_val = self._prepare_payment_dict(payment)
    #                 if dup_val == 0:
    #                     _logger.info('<---------Payment Amount is Zero----------> ')
    #                     continue
    #                 if invoice.state == 'draft':
    #                     _logger.info('<---------Invoice is going to open state----------> %s', invoice)
    #                     if invoice.invoice_line_ids:
    #                         invoice.action_post()
    #                 vals.update({'ref': invoice.name})
    # vals.update({'reconciled_invoice_ids': [(4, invoice.id, None)]})
    #
    #                 if 'journal_id' not in dup_val:
    #                     get_payments = self.env['account.payment'].search([])
    #                     for pay in get_payments:
    #                         if pay.invoice_ids:
    #                             for inv in pay.invoice_ids:
    #                                 if inv.id == invoice.id:
    #                                     if pay.journal_id:
    #                                         dup_val.update({'journal_id': pay.journal_id.id})
    #
    #                 if invoice.partner_id.customer_rank:
    #                     dup_val.update({'payment_type': 'inbound'})
    #                     payment_obj = self.search([('qbo_payment_id', '=', payment.get("Id"))], limit=1)
    #                 elif invoice.partner_id.supplier_rank:
    #                     dup_val.update({'payment_type': 'outbound'})
    #                     payment_obj = self.search([('qbo_bill_payment_id', '=', payment.get("Id"))], limit=1)
    #
    #                 if not payment_obj:
    #                     if 'journal_id' not in dup_val:
    #                         raise ValidationError(_('Payment Journal required'))
    # create payment
    # payment_obj = self.create(vals)
    # payment_obj.action_post()
    #
    #
    #                     register_payments = self.env['account.payment.register'].with_context(active_model='account.move',
    #                                                                                           active_ids=invoice.id).create(dup_val)
    #
    #                     payment_obj = register_payments._create_payments()
    #                     payment_obj.sudo().write(vals)
    #                     payment_obj.action_post()
    #                     payment_obj._cr.commit()
    #                     if payment_obj:
    #
    #                         if is_customer:
    #                             company.sudo().write({'last_imported_payment_id':payment_obj.qbo_payment_id})
    #                             company._cr.commit()
    #
    #                         elif is_vendor:
    #
    #                             company.sudo().write({'last_imported_bill_payment_id': payment_obj.qbo_bill_payment_id})
    #                             company._cr.commit()
    #
    #                 _logger.info(_("Payment created sucessfully! Payment Id: %s" % (payment_obj.id)))
    #     return payment_obj

    @api.model
    def get_linked_vendor_bill_ref(self, quickbook_id):
        qbo_id = str(quickbook_id)
        company = self.env['res.users'].search(
            [('id', '=', self._uid)]).company_id
        url_str = company.get_import_query_url()
        url = url_str.get('url') + '/bill/' + qbo_id + \
              '?minorversion=' + url_str.get('minorversion')
        result = requests.request('GET', url, headers=url_str.get('headers'))
        if result.status_code == 200:
            return True
        else:
            return False

    @api.model
    def _prepare_export_payment_dict(self):
        '''
        This method will prepare values
        for exporting payment into Quickbooks
        '''
        _logger.info("Preparing payment dictionary")
        log = None
        payment = self
        vals = {}
        vals = {
            'TotalAmt': payment.amount,
            'TxnDate': str(payment.date)
        }
        if payment.ref:
            invoice_obj = self.env['account.move'].search([('name','=',payment.ref)],limit=1)
            if invoice_obj.qbo_invoice_id:
                if invoice_obj.move_type == 'out_invoice':
                    txntype = "Invoice"
                # elif invoice_obj.move_type == 'in_invoice':
                #     txntype = "Bill"
                    vals.update({"Line": [
                    {
                        "Amount": payment.amount,
                        "LinkedTxn": [
                            {
                                "TxnId": invoice_obj.qbo_invoice_id,
                                "TxnType": txntype
                            }
                        ]
                    }
                ]})

            else:
                raise ValidationError(
                    _(f"invoice {invoice_obj.name} not Exported for the Payment {payment.name}"))



        if payment.payment_type == 'inbound' and payment.partner_type == 'customer':
            _logger.info("Customer Payment is being exported")
            vals.update({'CustomerRef': {'value': self.env['res.partner'].get_qbo_partner_ref(payment.partner_id)},
                         'PaymentRefNum': payment.name})
        elif payment.payment_type == 'outbound' and payment.partner_type == 'supplier':
            _logger.info("Vendor Payment is being exported")
            # Search for the associated vendor bill in account.move
            linked_vendor_payment_bill = self.env['account.move'].search(
                [('id', '=', payment.reconciled_bill_ids.id)])
            _logger.info(
                "LINKED VENDOR PAYMENT BILL IS ---> {}".format(linked_vendor_payment_bill))
            if linked_vendor_payment_bill:
                vals.update({
                    'VendorRef': {'value': self.env['res.partner'].get_qbo_partner_ref(payment.partner_id)},
                    'PayType': 'Check',
                    'DocNumber': payment.name,
                })
                if linked_vendor_payment_bill.qbo_invoice_id and linked_vendor_payment_bill.move_type == 'in_invoice':
                    _logger.info("QBO ID IS PRESENT TO VENDOR BILL")
                    # 2.TO CHECK IF VENDOR BILL IS PRESENT IN QBO
                    linked_vendor_bill = self.get_linked_vendor_bill_ref(
                        linked_vendor_payment_bill.qbo_invoice_id)
                    if linked_vendor_bill:
                        _logger.info("VENDOR BILL IS PRESENT IN QBO")
                        # UPDATE LINKED TRANSACTION DETAILS
                        vals.update({
                            "Line": [
                                {
                                    "Amount": payment.amount,
                                    "LinkedTxn": [
                                        {
                                            "TxnId": linked_vendor_payment_bill.qbo_invoice_id,
                                            "TxnType": "Bill"
                                        }
                                    ]
                                }
                            ]})
                    else:
                        _logger.info("VENDOR BILL NOT PRESENT IN QBO")
                        log = self.env['qbo.logger'].create({
                            'odoo_name': payment.name,
                            'odoo_object': 'Account Payment',
                            'message': f"Vendor Bill: {linked_vendor_payment_bill.name}  is not present in  Quickbooks.",
                            'created_date': datetime.now(),
                        })
                        # raise ValidationError(
                        #     _("Vendor Bill: %s  is not present in  Quickbooks." % (linked_vendor_payment_bill.name)))
                else:
                    _logger.info(
                        "Linked Vendor Bill is not exported to Quickbooks")
                    log = self.env['qbo.logger'].create({
                        'odoo_name': payment.name,
                        'odoo_object': 'Account Payment',
                        'message': f"Vendor Bill : {linked_vendor_payment_bill.name} linked to this Payment is not exported to Quickbooks.Please export Vendor Bill first to link the payment into Quickbooks ",
                        'created_date': datetime.now(),
                    })
                    # raise ValidationError(
                    #     _("Vendor Bill : %s linked to this Payment is not exported to Quickbooks.Please export Vendor Bill first to link the payment into Quickbooks " % (
                    #         linked_vendor_payment_bill.name)))

                if payment.qbo_paytype == 'check':
                    _logger.info("PAYTYPE SELECTED IS CHECK")
                    bankacc = payment.qbo_bankacc_ref_name
                    if not bankacc:
                        log = self.env['qbo.logger'].create({
                            'odoo_name': payment.name,
                            'odoo_object': 'Account Payment',
                            'message': f"Please add Bank Account Reference Name.",
                            'created_date': datetime.now(),
                        })
                        # raise ValidationError(
                        #     _("Please add Bank Account Reference Name."))
                    if not bankacc.qbo_id:
                        log = self.env['qbo.logger'].create({
                            'odoo_name': payment.name,
                            'odoo_object': 'Account Payment',
                            'message': f"The Account :{bankacc.name} is not yet exported to Quickbooks.Please export the Bank Account Reference first in order to proceed.",
                            'created_date': datetime.now(),
                        })
                        #
                        # raise ValidationError(
                        #     _("The Account :%s is not yet exported to Quickbooks.Please export the Bank Account Reference first in order to proceed." % (
                        #         bankacc.name)))

                    vals.update({
                        "CheckPayment": {
                            "BankAccountRef": {
                                "name": bankacc.name,
                                "value": bankacc.qbo_id
                            }
                        }
                    })
                elif payment.qbo_paytype == 'credit_card':
                    _logger.info("PAYTYPE SELECTED IS OF TYPE CREDIT CARD")
                    bankacc = payment.qbo_cc_ref_name
                    if not bankacc:
                        log = self.env['qbo.logger'].create({
                            'odoo_name': payment.name,
                            'odoo_object': 'Account Payment',
                            'message': f"Please add CC Account Reference Name.",
                            'created_date': datetime.now(),
                        })
                        # raise ValidationError(
                        #     _("Please add CC Account Reference Name."))
                    if not bankacc.qbo_id:
                        log = self.env['qbo.logger'].create({
                            'odoo_name': payment.name,
                            'odoo_object': 'Account Payment',
                            'message': f"he Account :{bankacc.name} is not yet exported to Quickbooks.Please export the CCAccount Reference first in order to proceed.",
                            'created_date': datetime.now(),
                        })
                        # raise ValidationError(
                        #     _("The Account :%s is not yet exported to Quickbooks.Please export the CCAccount Reference first in order to proceed." % (
                        #         bankacc.name)))

                    vals.update({
                        "CreditCardPayment": {
                            "CCAccountRef": {
                                "name": bankacc.name,
                                "value": bankacc.qbo_id
                            }
                        }
                    })

                else:
                    _logger.info("NO PAYTYPE SELECTED")
                    log = self.env['qbo.logger'].create({
                        'odoo_name': payment.name,
                        'odoo_object': 'Account Payment',
                        'message': f"Please select QBO Paytype in order to export the payment{payment.name}",
                        'created_date': datetime.now(),
                    })
                    # raise ValidationError(
                    #     _(f"Please select QBO Paytype in order to export the payment.---> {payment.name}"))

            else:
                _logger.info("The Payment is not linked to any vendor bill")
                log = self.env['qbo.logger'].create({
                    'odoo_name': payment.name,
                    'odoo_object': 'Account Payment',
                    'message': f"The Payment is not linked to any vendor bill{payment.name}",
                    'created_date': datetime.now(),
                })
                # raise ValidationError(
                #     _(f"The Payment is not linked to any vendor bill.Hence,cannot be exported to QBO---> {payment.name}"))

        else:
            _logger.info(
                "Other payments are not supported to be exported to QBO!")
        if log:
            return False
        else:
            return vals

    @api.model
    def export_to_qbo(self):
        """export account payment to QBO"""
        quickbook_config = self.env['res.users'].search(
            [('id', '=', self._uid)]).company_id
        if not quickbook_config:
            quickbook_config = self.env.company
        access_token = None
        realmId = None
        if quickbook_config.access_token:
            access_token = quickbook_config.access_token
        if quickbook_config.realm_id:
            realmId = quickbook_config.realm_id

        if self._context.get('active_ids'):
            payments = self.browse(self._context.get('active_ids'))
        else:
            payments = self

        for payment in payments:
            if len(payments) == 1:
                if payment.qbo_payment_id:
                    raise ValidationError(
                        _("Customer Payment  is already exported to QBO. Please, export a different payment."))
                if payment.qbo_bill_payment_id:
                    raise ValidationError(
                        _("Vendor Payment is already exported to QBO. Please, export a different payment."))

            if not payment.qbo_payment_id:
                if payment.state == 'posted':
                    vals = payment._prepare_export_payment_dict()
                    parsed_dict = json.dumps(vals)

                    if access_token and vals:
                        headers = {}
                        headers['Authorization'] = 'Bearer ' + \
                                                   str(access_token)
                        headers['Content-Type'] = 'application/json'
                        if payment.payment_type == 'inbound':
                            result = requests.request('POST', quickbook_config.url + str(realmId) + "/payment",
                                                      headers=headers, data=parsed_dict)
                        elif payment.payment_type == 'outbound':
                            result = requests.request('POST', quickbook_config.url + str(realmId) + "/billpayment",
                                                      headers=headers, data=parsed_dict)

                        if result.status_code == 200:
                            response = quickbook_config.convert_xmltodict(
                                result.text)
                            # update QBO payment id
                            if payment.payment_type == 'inbound' and payment.partner_type == 'customer':
                                payment.qbo_payment_id = response.get(
                                    'IntuitResponse').get('Payment').get('Id')
                                self._cr.commit()
                            elif payment.payment_type == 'outbound' and payment.partner_type == 'supplier':
                                payment.qbo_bill_payment_id = response.get('IntuitResponse').get('BillPayment').get(
                                    'Id')
                                self._cr.commit()
                            _logger.info(
                                _("%s exported successfully to QBO" % (payment.name)))
                        else:
                            _logger.error(
                                _("[%s] %s" % (result.status_code, result.reason)))
                            raise ValidationError(
                                _("[%s] %s %s" % (result.status_code, result.reason, result.text)))
                        #                         return False
                else:
                    if len(payments) == 1:
                        if payment.partner_type == 'customer':
                            raise ValidationError(
                                _("Only posted state Customer Payments is exported to QBO."))
                        if payment.partner_type == 'supplier':
                            raise ValidationError(
                                _("Only posted state Vendor Payments is exported to QBO."))


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    #     qbo_payment_method_id = fields.Many2one('qbo.payment.method', string='QBO Payment Method', help='QBO payment method reference, used in payment import from QBO.')

    def get_journal_from_account(self, qbo_account_id):
        account_id = self.env[
            'account.account'].get_account_ref(qbo_account_id)
        account = self.env['account.account'].browse(account_id)
        journal_id = self.search(
            [('type', 'in', ['bank', 'cash']), ('default_account_id', '=', account_id)], limit=1)
        if not journal_id:
            raise ValidationError(
                _("Please, define payment journal for Account Name : %s " % (account.name)))

        return journal_id.id

# AccountJournal()
