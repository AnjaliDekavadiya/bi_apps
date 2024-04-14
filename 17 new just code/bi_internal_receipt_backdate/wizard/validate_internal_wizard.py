# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime,date, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class wizard_validate_internal_transfer(models.TransientModel):
	_name = 'wizard.validate.internal.transfer'
	_description="wizard validate internal transfer"

	transfer_date = fields.Datetime('BackDate',required=True)
	transfer_remark = fields.Char('Remark',required=True)

	def backdateorder_button(self):
		today = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
		back_date = self.transfer_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
		
		if back_date >= today:
			raise UserError(_('Please Enter Correct Back Date.'))

		active_models1 = self._context.get('active_model')
		if active_models1 == 'stock.picking':
			custom_stock_picking_ids = self.env['stock.picking'].browse(self._context.get('active_id'))
			
			for picking in custom_stock_picking_ids.filtered(lambda x: x.state not in ('cancel')):
				for data in picking.move_ids:
					data.write({'date':self.transfer_date,'move_remark': self.transfer_remark,'move_date':self.transfer_date})
					accounts_data = data.product_id.product_tmpl_id.get_product_accounts()
					acc_valuation = accounts_data.get('stock_valuation', False)
					
					if custom_stock_picking_ids.picking_type_id.code == 'internal':
						for category in data.product_id.categ_id:
							if category.property_valuation != 'real_time':
								custom_accountmove = self.env['account.move'].create({'date':self.transfer_date,
									'journal_id':data.product_id.categ_id.property_stock_journal.id,
									'ref':data.location_id.name,
									# 'partner_id':data.picking_partner_id.id,
									'stock_move_id':data.id})

								self.env['account.move.line'].create({
													'partner_id':custom_accountmove.partner_id.id,
													'account_id':1,
													'name':'Transfer',
													'move_id':custom_accountmove.id
													})

								custom_accountmove.action_post()

					elif custom_stock_picking_ids.picking_type_id.code == 'incoming':
						for category in data.product_id.categ_id:
							if category.property_valuation != 'real_time':
								custom_accountmove = self.env['account.move'].create({'date':self.transfer_date,
									'journal_id':data.product_id.categ_id.property_stock_journal.id,
									'ref':data.location_id.name,
									# 'partner_id':data.picking_partner_id.id,
									'stock_move_id':data.id})

								self.env['account.move.line'].create({
													'partner_id':custom_accountmove.partner_id.id,
													'account_id':1,
													'name':'Transfer',
													'move_id':custom_accountmove.id
													})

								custom_accountmove.action_post()

					for line in data.mapped('move_line_ids'):
						line.write({'date': self.transfer_date})

			return custom_stock_picking_ids.button_validate()

		elif active_models1 == 'stock.picking.type':
			custom_stock_picking_ids = self.env['stock.picking'].browse(self._context.get('active_id'))
			stock_type_id = self.env['stock.picking.type'].browse(self._context.get('active_id'))
			stock_picking_type = self.env['stock.picking'].search([('picking_type_id','=',stock_type_id.id)],
				order='id desc',limit=1)
			for picking in stock_picking_type:
				for data in picking.move_ids:
					data.write({'date':self.transfer_date,'move_remark': self.transfer_remark,'move_date':self.transfer_date})
					for line in data.mapped('move_line_ids'):
						line.write({'date': self.transfer_date})
					if stock_type_id.code == 'internal':
						for category in data.product_id.categ_id:
							if category.property_valuation != 'real_time':
								custom_accountmove = self.env['account.move'].create({'date':self.transfer_date,
									'journal_id':data.product_id.categ_id.property_stock_journal.id,
									'ref':data.location_id.name,
									# 'partner_id':data.picking_partner_id.id,
									'stock_move_id':data.id})

								self.env['account.move.line'].create({
													'partner_id':custom_accountmove.partner_id.id,
													'account_id':1,
													'name':'Transfer',
													'move_id':custom_accountmove.id
													})

								custom_accountmove.action_post()

					elif stock_type_id.code == 'incoming':
						for category in data.product_id.categ_id:
							if category.property_valuation != 'real_time':
								custom_accountmove = self.env['account.move'].create({'date':self.transfer_date,
									'journal_id':data.product_id.categ_id.property_stock_journal.id,
									'ref':data.location_id.name,
									# 'partner_id':data.picking_partner_id.id,
									'stock_move_id':data.id})

								self.env['account.move.line'].create({
												'partner_id':custom_accountmove.partner_id.id,
												'account_id':1,
												'name':'Transfer',
												'move_id':custom_accountmove.id
												})

								custom_accountmove.action_post()

			return stock_picking_type.button_validate()


		elif active_models1 == 'purchase.order':
			custom_stock_picking_ids = self.env['stock.picking'].browse(self._context.get('active_id'))
			custom_purchase_ids = self.env['purchase.order'].browse(self._context.get('active_id'))
			for custom_purchase_stock in self.env['stock.picking'].search([('purchase_id','=',custom_purchase_ids.id)]):
				for picking in custom_purchase_stock:
					for data in picking.move_ids:
						data.write({'move_remark':self.transfer_remark,'date':self.transfer_date,
							'move_date':self.transfer_date})
						for line in data.mapped('move_line_ids'):
							line.write({'date': self.transfer_date})
						for category in data.product_id.categ_id:
							if category.property_valuation != 'real_time':
								custom_accountmove = self.env['account.move'].create({'date':self.transfer_date,
									'journal_id':data.product_id.categ_id.property_stock_journal.id,
									'ref':data.location_id.name,
									# 'partner_id':data.picking_partner_id.id,
									'stock_move_id':data.id})

								self.env['account.move.line'].create({
													'partner_id':custom_accountmove.partner_id.id,
													'account_id':1,
													'name':'Transfer',
													'move_id':custom_accountmove.id
													})

								custom_accountmove.action_post()

				return custom_purchase_stock.button_validate()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: