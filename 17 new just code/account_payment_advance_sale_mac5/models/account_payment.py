from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    advance_sale_id = fields.Many2one('sale.order', string="Sales Order", readonly=True)

    @api.constrains("partner_id", "advance_sale_id")
    def _check_partner_invoice_advance_payments(self):
        if self.filtered(lambda x: x.advance_sale_id
                                   and x.partner_id != x.advance_sale_id.partner_invoice_id):
            raise ValidationError(_("Customer should be the same as the Invoice Address in sales"))
