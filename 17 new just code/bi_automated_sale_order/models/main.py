# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import date,datetime
from odoo.exceptions import UserError, ValidationError

class AutomatedSaleOrder(models.Model):
	_name = "automated.sale"
	_description = "Automated Sale"

	name = fields.Char(string="Name")
	payment_journal = fields.Many2one("account.journal", string ="Payment Journal",domain=[['type', 'in',['bank','cash']]])
	company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
	sales_journal = fields.Many2one("account.journal",string="Sales Journal",
	domain="[('type', 'in',['sale']), ('company_id', '=', company_id)]")

	validation_order = fields.Boolean("Validation Order")
	validation_picking = fields.Boolean("Validation Picking")
	force_transfer = fields.Boolean("force transfer,even if is unavailable.")
	create_incoice = fields.Boolean("Create Invoice")
	validate_invoice = fields.Boolean("Vaidate Invoice")
	register_payment = fields.Boolean("Register Payment")
	force_invoice = fields.Boolean("Force Invoice Date")

	shipping_policy =fields.Selection([
		('direct', 'Deliver each product when available'),
		('one', 'Deliver all products at once')],
		string='Shipping Policy',required=True)
	invoicing_policy =  fields.Selection(
		[('order', 'Ordered quantities'),
		 ('delivery', 'Delivered quantities'),
		], string='Invoicing Policy',required=True)

	@api.onchange('force_invoice','validate_invoice','register_payment')
	def depends_force(self):
		if self.force_invoice == True:
			self.validate_invoice = True

		if self.validate_invoice == True:
			self.create_incoice = True

		if self.register_payment == True:
			self.validate_invoice = True
			
	
	@api.onchange('force_transfer','validation_picking')
	def depends_transfer(self):
		if self.force_transfer == True:
			self.validation_picking = True

		if self.validation_picking == True:
			self.validation_order = True

	@api.onchange('create_incoice')
	def depends_invoice(self):
		if self.create_incoice == True:
			self.validation_order = True
			self.validation_picking = True
			self.force_transfer = True

class InheritPartner(models.Model):
	_inherit = "res.partner"

	is_automated = fields.Boolean(string="Is automated Workflow")
	work_process_id = fields.Many2one("automated.sale",string="Workflow Process")


class InheritSale(models.Model):
	_inherit = "sale.order"

	is_related = fields.Boolean(related="partner_id.is_automated")
	work_process_order_id = fields.Many2one("automated.sale",string="Workflow Process")

	@api.onchange("partner_id")
	def change_workflow(self):
		self.work_process_order_id = self.partner_id.work_process_id

	def action_automate(self):
		
		if self.work_process_order_id:



			self.picking_policy = self.work_process_order_id.shipping_policy
			for line in self.order_line:
					line.product_id.invoice_policy = self.work_process_order_id.invoicing_policy
		

			if self.work_process_order_id.validation_order == True:
				picking_confirm=self.action_confirm()
				
				for order in self:
					if self.work_process_order_id.validation_picking == True or self.work_process_order_id.force_transfer == True:
						picking_obj = self.env['stock.picking'].search([('origin','=',order.name)])
						
						for pick in picking_obj:
							for qty in pick.move_ids:
								
								qty.write({
								'quantity' : qty.product_uom_qty
										})
						
							pick.button_validate()
							pick._action_done()
							

							for line in order.order_line:
								line.write({
									'qty_delivered' : line.product_uom_qty,
											})

							
					
						

			if self.work_process_order_id.create_incoice == True:

				
				
				create_invoice = self._create_invoices()
				

				invoice_obj = self.env['account.move'].search([('invoice_origin','=',self.name)])

				if self.work_process_order_id.sales_journal:
					invoice_obj.write({'journal_id' :self.work_process_order_id.sales_journal.id})

				payment =self.env['account.payment']

				payment_method = self.env['account.payment.method'].search([],limit=1)

				


				if self.work_process_order_id.register_payment == True and self.work_process_order_id.validate_invoice == True:
					validate=invoice_obj.action_post()

					if create_invoice:

						if create_invoice.state == 'posted' and create_invoice.payment_state == 'not_paid':
							pmt = self.env['account.payment.register'].with_context(active_model='account.move', active_ids=create_invoice.ids).create({})
							pmt._create_payments()

						else:
							print("!! Already Posted And Paid For ID!!",create_invoice)

				elif self.work_process_order_id.validate_invoice == True or self.work_process_order_id.force_invoice==True:
					validate=invoice_obj.action_post()
					
				else:
					pass
						
				
					


				
							 
		else:
			raise ValidationError(('Workflow Process is not given,Please give the Workflow process.') )

		
		