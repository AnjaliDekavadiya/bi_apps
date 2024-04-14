from gevent import config
from odoo import models, fields, api,_
from odoo.addons.payment.models.payment_provider import ValidationError
from odoo.tools.float_utils import float_compare


import logging
import pprint

_logger = logging.getLogger(__name__)


class PaymentPayLater(models.Model):
    _inherit = "payment.provider"

    code = fields.Selection(selection_add=[('paylater', 'Pay Later')], ondelete={'paylater': 'set default'})

    def paylater_form_generate_values(self, values):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        return values

    def paylater_get_form_action_url(self):
        return '/payment/paylater/feedback'

    def _get_feature_support(self):
        res = super(PaymentPayLater, self)._get_feature_support()
        res['authorize'].append('paylater')
        return res
class PaylaterPaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    """Default methode of the core"""
    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return Alipay-specific rendering values.
        Note: self.ensure_one() from `_get_processing_values`
        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of acquirer-specific processing values
        :rtype: dict
        """

        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'paylater':
            return res
        else:
            api_url = self.provider_id.paylater_get_form_action_url()
            record_currency = self.env['res.currency'].browse(processing_values.get('currency_id'))
            processing_values.update({'return_url':api_url,'payment_later_url':api_url,'currency':record_currency})
            return processing_values

    @api.model
    def _get_tx_from_notification_data(self, provider, data):
        tx = super()._get_tx_from_notification_data(provider, data)
        if provider != 'paylater':
            return tx
        reference, amount, currency_name = data.get('reference'), data.get('amount'), data.get('currency_name')
        tx = self.search([('reference', '=', reference)])
        if not tx or len(tx) > 1:
            error_msg = _('received data for reference %s') % (pprint.pformat(reference))
            if not tx:
                error_msg += _('; no order found')
            else:
                error_msg += _('; multiple order found')
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        return tx

    def _paylater_form_get_invalid_parameters(self, data):

        invalid_parameters = []

        if float_compare(float(data.get('amount', '0.0')), self.amount, 2) != 0:
            invalid_parameters.append(('amount', data.get('amount'), '%.2f' % self.amount))
        if data.get('currency') != self.currency_id.name:
            invalid_parameters.append(('currency', data.get('currency'), self.currency_id.name))

        return invalid_parameters

    def _process_notification_data(self, data):
        self.ensure_one()
        if self.provider_code != 'paylater':
            return
        config_setting = self.env['ir.default'].sudo()._get('res.config.settings','transaction_setting') or 'order_place'
        if config_setting == "order_place":
            self._set_done()
        else:
            self._set_pending()