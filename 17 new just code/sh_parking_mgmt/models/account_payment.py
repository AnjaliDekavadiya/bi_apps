# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, _, api
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'
    @api.model
    def create(self, vals):
        res= super(
                AccountPayment, self).create(vals)
        move_id = self.env['account.move'].sudo().search([('id', 'in', self.env.context.get('active_ids'))])
        if vals['amount']<move_id.sh_membership_id.company_id.sh_remaining_amount:
            raise UserError(_("Please Enter Minimum Amount :  %s") % move_id.sh_membership_id.company_id.sh_remaining_amount)
        return res

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    def action_create_payments(self):
        res= super(AccountPaymentRegister, self).action_create_payments()
        move_id = self.env['account.move'].sudo().search([('id', '=', self.env.context.get('active_id'))])
        if self.amount==move_id.amount_total:
            move_id.sh_membership_id.sh_member_amount_remaining+=self.amount
        elif self.amount<move_id.amount_total:
            move_id.sh_membership_id.sh_member_amount_remaining+=self.amount
        else:
            move_id.sh_membership_id.sh_member_amount_remaining+=move_id.amount_total
        return res
        