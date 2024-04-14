# coding: utf-8

from odoo import api, fields, models


class PaymentAcquire(models.Model):
#    _inherit = 'payment.acquirer'
    _inherit = 'payment.provider'

#    provider = fields.Selection(
    code = fields.Selection(
        selection_add=[('wallet', 'Wallet Money Pay')],
        ondelete={'wallet': 'set default'}
    )

#    def _get_default_payment_method_id(self):#V15
    def _get_default_payment_method_id(self, code):#V16
        self.ensure_one()
#        if self.provider != 'wallet':
        if code != 'wallet':
            return super()._get_default_payment_method_id()
        return self.env.ref('customer_website_wallet.payment_method_wallet').id
#    def wallet_get_form_action_url(self):
#        return '/payment/wallet/feedback'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
