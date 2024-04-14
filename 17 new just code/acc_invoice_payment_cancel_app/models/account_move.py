# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountMove(models.Model):
	_inherit = "account.move"

	def button_cancels(self):
		for move in self:
			if self.company_id.invoice_opration_type == 'cancel':
				move.button_cancel()
				payment_ids = self.env['account.payment'].search([('ref','ilike',move.name)])
				for payment in payment_ids:
					payment.button_cancels()
					payment.state = 'cancel'
				
			if self.company_id.invoice_opration_type == 'draft':
				move.button_cancel()
				payment_ids = self.env['account.payment'].search([('ref','ilike',move.name)])
				for payment in payment_ids:
					payment.button_cancels()
					payment.state = 'cancel'
				move.button_draft()
			if self.company_id.invoice_opration_type == 'delete':
				move.write({'posted_before':False})
				move.button_cancel()
				payment_ids = self.env['account.payment'].search([('ref','ilike',move.name)])
				for payment in payment_ids:
					payment.button_cancels()
					payment.state = 'cancel'
				move.button_draft()
				move.unlink()
				tree_view_id = self.env.ref('account.view_move_tree').id
				return {
					'name': _('Invoice'),
					'domain': [('move_type','=','out_invoice')],
					'type': 'ir.actions.act_window',
					'res_model': 'account.move',
					'view_type':'form',
					'view_mode' : 'tree',
					'view_id': tree_view_id,
					'res_id': self.id,
				}

	def account_move_cancel(self):
		account_id =self.env['account.move'].browse(self._context.get('active_ids'))
		for move in account_id:
			move.button_cancel()
			payment_ids = self.env['account.payment'].search([('ref','ilike',move.name)])
			for payment in payment_ids:
				payment.button_cancels()
				payment.state = 'cancel'
			
	def account_move_draft(self):
		account_id =self.env['account.move'].browse(self._context.get('active_ids'))
		for move in account_id:
			move.button_cancel()
			payment_ids = self.env['account.payment'].search([('ref','ilike',move.name)])
			for payment in payment_ids:
				payment.button_cancels()
				payment.state = 'cancel'
			move.button_draft()
			
	def account_move_delete(self):
		account_id =self.env['account.move'].browse(self._context.get('active_ids'))
		for move in account_id:
			move.write({'posted_before':False})
			move.button_cancel()
			payment_ids = self.env['account.payment'].search([('ref','ilike',move.name)])
			for payment in payment_ids:
				payment.button_cancels()
				payment.state = 'cancel'
			move.button_draft()
		account_id.unlink()             