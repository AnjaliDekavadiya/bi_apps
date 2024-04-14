from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_pos_smart_cash = fields.Boolean(string="Payment Terminal",
                                           help="The transactions are processed by payment terminal."
                                           " Set your terminal credentials on the related payment method.")

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        payment_methods = self.env['pos.payment.method']
        if not self.env['ir.config_parameter'].sudo().get_param('pos_smart_cash.module_pos_smart_cash'):
            payment_methods |= payment_methods.search(
                [('use_payment_terminal', '=', 'smart_cash')])
            payment_methods.write({'use_payment_terminal': False})
