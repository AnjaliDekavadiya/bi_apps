# coding: utf-8

import logging
import pprint
from datetime import datetime
from werkzeug import urls#V15

#from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.addons.customer_website_wallet.controllers.main import WalletController
_logger = logging.getLogger(__name__)


from odoo import api, fields, models, tools, _


class WalletPaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return Buckaroo-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of acquirer-specific processing values
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
#        if self.provider != 'wallet':
        if self.provider_code != 'wallet':
            return res

#        return_url = urls.url_join(self.acquirer_id.get_base_url(), WalletController._return_url)
        return_url = urls.url_join(self.provider_id.get_base_url(), WalletController._return_url)
        rendering_values = {
            'api_url': return_url,
            'wallet_amount': self.amount,
            'wallet_currency': self.currency_id.name,
            'wallet_reference': self.reference,
            # Include all 4 URL keys despite they share the same value as they are part of the sig.
            'wallet_return': return_url,
            'wallet_returncancel': return_url,
            'wallet_returnerror': return_url,
            'wallet_returnreject': return_url,
        }
        return rendering_values
    
    def _get_tx_from_notification_data(self, provider, notification_data):#16
        """ Override of payment to find the transaction based on Wallet data.

        :param str provider: The provider of the acquirer that handled the transaction
        :param dict notification_data: The notification data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if inconsistent data were received
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_notification_data(provider, notification_data)
        if provider != 'wallet' or len(tx) == 1:
            return tx

        reference = notification_data.get('wallet_reference')

        tx = self.search([('reference', '=', reference), ('provider_code', '=', 'wallet')])
        if not tx:
            raise ValidationError(
                "Wallet: " + _("No transaction found matching reference %s.", reference)
            )

        return tx
    
    def _process_notification_data(self, notification_data):
        """ Override of payment to process the transaction based on COD data.

        Note: self.ensure_one()

        :param dict notification_data: The notification data sent by the provider
        :return: None
        :raise: ValidationError if inconsistent data were received
        """
        super()._process_notification_data(notification_data)
        if self.provider_code != 'wallet':#V16
            return
        _logger.info('Validated cod payment for tx %s: set as pending' % (self.reference))
        if notification_data.get('sale_order_id', False):
            order = self.env['sale.order'].sudo().browse(notification_data.get('sale_order_id'))
        else:
#            order = self.env['sale.order'].sudo().search([('name', '=', data.get('reference'))])
            order = self.env['sale.order'].sudo().search([('name', '=', notification_data.get('wallet_reference'))])
        if order and order.partner_id.wallet_balance >= order.amount_total:
            vals = {
                'customer_id': order.partner_id.id,
                'date': fields.Datetime.now(),
                'amount': order.amount_total,
                'currency_id': order.currency_id.id,
                'company_id': order.company_id.id,
                'balance_type': 'debit',
            }
            custom = self.env['customer.wallet'].sudo().create(vals)
            order.write({'wallet_transaction_id': custom.id, 'wallet_used': order.amount_total})
            custom.action_done()
        
        
        self._set_done()

#    @api.model
#    def _wallet_form_get_tx_from_data(self, data):
    def _get_tx_from_feedback_data(self, provider, data):
#        reference, amount, currency_name = data.get('reference'), data.get('amount'), data.get('currency_name')
        tx = super()._get_tx_from_feedback_data(provider, data)
        if provider != 'wallet':
            return tx

        reference, amount, currency_name = data.get('wallet_reference'), data.get('wallet_amount'), data.get('wallet_currency')
#        tx = self.search([('reference', '=', reference)])
        tx = self.search([('reference', '=', reference), ('provider', '=', 'wallet')])#V15

        if not tx or len(tx) > 1:
            error_msg = _('received data for reference %s') % (pprint.pformat(reference))
            if not tx:
                error_msg += _('; no order found')
            else:
                error_msg += _('; multiple order found')
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        return tx

#    def _wallet_form_get_invalid_parameters(self, data):
#        invalid_parameters = []

#        if float_compare(float(data.get('amount', '0.0')), self.amount, 2) != 0:
#            invalid_parameters.append(('amount', data.get('amount'), '%.2f' % self.amount))
#        if data.get('currency') != self.currency_id.name:
#            invalid_parameters.append(('currency', data.get('currency'), self.currency_id.name))

#        return invalid_parameters

#    def _wallet_form_validate(self, data):
    def _process_feedback_data(self, data):
        super()._process_feedback_data(data)#V15
#        if self.provider != 'wallet':#V15
        if self.provider_code != 'wallet':
            return
        _logger.info('Validated wallet payment for tx %s: set as pending' % (self.reference))
        if data.get('sale_order_id', False):
            order = self.env['sale.order'].sudo().browse(data.get('sale_order_id'))
        else:
#            order = self.env['sale.order'].sudo().search([('name', '=', data.get('reference'))])
            order = self.env['sale.order'].sudo().search([('name', '=', data.get('wallet_reference'))])
        if order and order.partner_id.wallet_balance >= order.amount_total:
            vals = {
                'customer_id': order.partner_id.id,
                'date': fields.Datetime.now(),
                'amount': order.amount_total,
                'currency_id': order.currency_id.id,
                'company_id': order.company_id.id,
                'balance_type': 'debit',
            }
            custom = self.env['customer.wallet'].sudo().create(vals)
            order.write({'wallet_transaction_id': custom.id, 'wallet_used': order.amount_total})
            custom.action_done()
        self._set_done()
#        return self.write({'state': 'done', 'date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
