# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountPayment(models.Model):
	_inherit = "account.payment"

	def button_cancels(self):
		for payment in self:
			if self.company_id.payment_opration_type == 'cancel':
				payment.action_cancel()
			if self.company_id.payment_opration_type == 'draft':
				payment.action_cancel()
				payment.action_draft()
			if self.company_id.payment_opration_type == 'delete':
				payment.action_cancel()
				payment.unlink()
				tree_view_id = self.env.ref('account.view_account_payment_tree').id
				return {
					'name': _('Payment'),
					'type': 'ir.actions.act_window',
					'res_model': 'account.payment',
					'view_type':'form',
					'view_mode': 'tree',
					'view_id': tree_view_id,
					'res_id': self.id,
				}


	def account_payment_cancel(self):
		account_id =self.env['account.payment'].browse(self._context.get('active_ids'))
		for payment in account_id:
			payment.action_cancel()
			
	def account_payment_draft(self):
		account_id =self.env['account.payment'].browse(self._context.get('active_ids'))
		for payment in account_id:
			payment.action_cancel()
			payment.action_draft()
			
	def account_payment_delete(self):
		account_id =self.env['account.payment'].browse(self._context.get('active_ids'))
		for payment in account_id:
			payment.action_cancel()
		account_id.unlink()