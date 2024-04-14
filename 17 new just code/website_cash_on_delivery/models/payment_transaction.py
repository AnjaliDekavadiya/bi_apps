# coding: utf-8

import logging
import pprint

#from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare
_logger = logging.getLogger(__name__)

from werkzeug import urls

from odoo import api, fields, models, tools, _
from odoo.addons.website_cash_on_delivery.controllers.main import CodController


class CodPaymentTransaction(models.Model):
    _inherit = 'payment.transaction'


    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return Buckaroo-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of acquirer-specific processing values
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'cod':
            return res

#        return_url = urls.url_join(self.acquirer_id.get_base_url(), CodController._return_url)
        return_url = urls.url_join(self.provider_id.get_base_url(), CodController._accept_url)
        rendering_values = {
            'api_url': return_url,
            'amount': self.amount,
            'currency': self.currency_id,
            'reference': self.reference,
            # Include all 4 URL keys despite they share the same value as they are part of the sig.
            'return': return_url,
            'returncancel': return_url,
            'returnerror': return_url,
            'returnreject': return_url,
        }
        return rendering_values

    def _get_tx_from_notification_data(self, provider, notification_data):#16
        """ Override of payment to find the transaction based on COD data.

        :param str provider: The provider of the acquirer that handled the transaction
        :param dict notification_data: The notification data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if inconsistent data were received
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_notification_data(provider, notification_data)
        if provider != 'cod' or len(tx) == 1:
            return tx

        reference = notification_data.get('reference')
#        txn_id = notification_data.get('trade_no')
#        if not reference or not txn_id:
#        if not reference:
#            raise ValidationError(
#                "COD: " + _(
#                    "Received data with missing reference %(r)s or txn_id %(t)s.",
#                    r=reference, t=txn_id
#                )
#            )

        tx = self.search([('reference', '=', reference), ('provider_code', '=', 'cod')])
        if not tx:
            raise ValidationError(
                "COD: " + _("No transaction found matching reference %s.", reference)
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
        if self.provider_code != 'cod':#V16
            return
        _logger.info('Validated cod payment for tx %s: set as pending' % (self.reference))
        self._set_done()

    def _log_received_message(self):
        """ Override of `payment` to remove custom providers from the recordset.

        :return: None
        """
        other_provider_txs = self.filtered(lambda t: t.provider_code != 'cod')
        super(CodPaymentTransaction, other_provider_txs)._log_received_message()

    def _get_sent_message(self):
        """ Override of payment to return a different message.

        :return: The 'transaction sent' message
        :rtype: str
        """
        message = super()._get_sent_message()
        if self.provider_code == 'cod':
            message = _(
                "The customer has selected %(provider_name)s to make the payment.",
                provider_name=self.provider_id.name
            )
        return message

#    @api.model
#    def _cod_form_get_tx_from_data(self, data):
#        reference, amount, currency_name = data.get('reference'), data.get('amount'), data.get('currency_name')
#        tx = self.search([('reference', '=', reference)])

#        if not tx or len(tx) > 1:
#            error_msg = _('received data for reference %s') % (pprint.pformat(reference))
#            if not tx:
#                error_msg += _('; no order found')
#            else:
#                error_msg += _('; multiple order found')
#            _logger.info(error_msg)
#            raise ValidationError(error_msg)

#        return tx

#    def _cod_form_get_invalid_parameters(self, data):
#        invalid_parameters = []
#        if float_compare(float(data.get('amount', '0.0')), self.amount, 2) != 0:
#            invalid_parameters.append(('amount', data.get('amount'), '%.2f' % self.amount))
#        if data.get('currency') != self.currency_id.name:
#            invalid_parameters.append(('currency', data.get('currency'), self.currency_id.name))

#        return invalid_parameters

#    def _cod_form_validate(self, data):
#        _logger.info('Validated cod payment for tx %s: set as pending' % (self.reference))
##         return self.write({'state': 'done'})
#        return self._set_transaction_done()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
