# -*- coding: utf-8 -*-

from odoo import fields, models


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    def _get_payment_terminal_selection(self):
        return super(PosPaymentMethod, self)._get_payment_terminal_selection() + [('smart_cash', 'Smart Cash')]

   # credentials
    pos_smart_cash = fields.Boolean(string="SmartCash", default=True)

class ResConfigSettings(models.Model):
    _inherit = 'pos.config'

    gateway_ip = fields.Char(string='Gatway Ip')
    port_ip = fields.Char(string='Port Ip')
    direct_print_receipt = fields.Boolean(string='Direct Print Receipt ?')
