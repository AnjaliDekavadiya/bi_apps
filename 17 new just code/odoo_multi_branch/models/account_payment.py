# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = "account.payment"

    company_branch_id = fields.Many2one(
        'res.company.branch',
        string="Branch",
        copy=False,
        tracking=True,
        default=lambda self: self.env.user.company_branch_id.id,
    )

    @api.model
    def default_get(self, default_fields):
        rec = super(AccountPayment, self).default_get(default_fields)
#        invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
        if self._context.get('active_model') and self._context.get('active_model')  == 'account.move':
            invoice_defaults = self.env[self._context.get('active_model')].browse(self._context.get('active_ids', False))
            if invoice_defaults and len(invoice_defaults) == 1 and rec:
                invoice = invoice_defaults[0]
                try:
                    rec.update({'company_branch_id' : invoice['company_branch_id'][0].id})
                except:
                    pass
        return rec

#    def _create_payment_entry(self, amount): odoo13
#        rec = super(AccountPayment, self)._create_payment_entry(amount)
#        for line in rec.line_ids:
#            line.update({'company_branch_id' : self.company_branch_id.id})
#        return rec
       
    #odoo13
#    def post(self):
    def action_post(self):
        rec = super(AccountPayment, self.with_context({'payment_branch_spl_custom' : self.company_branch_id.id})).action_post()
        return rec

#    def _get_move_vals(self, journal=None): odoo13
#        move_vals = super(AccountPayment, self)._get_move_vals(journal=journal)
#        move_vals.update({'company_branch_id':self.company_branch_id.id})
#        return move_vals

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
