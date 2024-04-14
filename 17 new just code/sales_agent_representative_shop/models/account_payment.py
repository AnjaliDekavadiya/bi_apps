#from odoo import models, fields, api


#class AccountPayment(models.Model):
#    _inherit = 'account.payment'

#    custom_webshop_add_agent = fields.Boolean(
#        string='Added Agent'
#    )

#    @api.model
#    def default_get(self, fields):
#        rec = super(AccountPayment, self).default_get(fields)
#        invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
#        if invoice_defaults and len(invoice_defaults) == 1:
#            invoice = invoice_defaults[0]
#            if invoice.get('sale_commission_user_ids') and invoice.get('custom_webshop_add_agent'):
#                sale_commission_user_ids = self.env['sale.commission.level.users'].browse(invoice.get('sale_commission_user_ids'))
#                sale_commission_user_lines = []
#                for commission in sale_commission_user_ids:
#                    sale_commission_user_lines.append((0, 0, {
#                        'level_id': commission.level_id.id,
#                        'user_id': commission.user_id and commission.user_id.id or False}))
#                rec['sale_commission_user_ids'] = sale_commission_user_lines
#                rec['custom_webshop_add_agent'] = invoice.get('custom_webshop_add_agent', False)
#        return rec
