# -*- coding: utf-8 -*-

from odoo import models, fields, exceptions, api, _
from odoo.exceptions import ValidationError,UserError
from datetime import datetime ,date

class ReccuringPayments(models.TransientModel):
	_name = 'reccuring.payments' 
	_description = 'Reccuring Payments'


	start_date = fields.Date(string="Start Date" , default=fields.Datetime.now)
	entries_line_ids = fields.One2many('remain.entries.lines', 'reccuring_payment_id', 'Remain Entries Line')

	
	@api.model
	def default_get(self , fields):
		res = super(ReccuringPayments, self).default_get(fields)
		recurring_templates = self.env['recurring.templates'].search([])
		entries_lines=[]
		for templates in recurring_templates:
			entries_lines.append((0,0, {
					'date':templates.start_date,
					'name': templates.name,
					'amount': templates.amount,
					'credit_account_id' : templates.credit_account_id.id,
					'debit_account_id' : templates.debit_account_id.id,
					'journal_id' : templates.journal_id.id,
					'generate_journal' :templates.generate_journal,
				}))
		res.update({
			'entries_line_ids': entries_lines
		})
		return res

	@api.onchange('start_date')
	def chnage_start_date(self):

		recurring_templates = self.env['recurring.templates'].search([('start_date','>=',self.start_date),('states','=','running')])
		recurring_lines=[]
		for template in recurring_templates:
			recurring_lines.append((0,0, {
					'date':template.start_date,
					'name': template.name,
					'amount': template.amount,
					'credit_account_id' : template.credit_account_id.id,
					'debit_account_id' : template.debit_account_id.id,
					'journal_id' : template.journal_id.id,
					'generate_journal' :template.generate_journal,
				}))
			self.update({'entries_line_ids':False})
		self.update({"entries_line_ids" : recurring_lines})
		

	def action_generate_entries(self):
		for lines in self.entries_line_ids:
			if lines.generate_journal == "unposted":
				account_move = self.env['account.move']
				credit_line = [0,0,{
								'account_id' : lines.credit_account_id.id,
								'name' : 'Recurring Entry',
								'debit' : 0.0,
								'credit' : lines.amount,
								}]
				debit_line = [0,0,{
								'account_id' : lines.debit_account_id.id,
								'name' : 'Recurring Entry',
								'debit' : lines.amount,
								'credit' : 0.0
								}]
				move_line = [credit_line ,debit_line]
				jounral = self.env['account.move'].create(
					{'name': '/',
					'date': lines.date,
					'journal_id' :lines.journal_id.id,
					'ref' : lines.name,
					'line_ids' : move_line,
					})
			if lines.generate_journal == "posted":
				account_move = self.env['account.move']
				credit_line = [0,0,{
								'account_id' : lines.credit_account_id.id,
								'name' : 'Recurring Entry',
								'debit' : 0.0,
								'credit' : lines.amount,
								}]
				debit_line = [0,0,{
								'account_id' : lines.debit_account_id.id,
								'name' : 'Recurring Entry',
								'debit' : lines.amount,
								'credit' : 0.0
								}]
				move_line = [credit_line ,debit_line]
				jounral = self.env['account.move'].create(
					{'name': '/',
					'date': lines.date,
					'journal_id' :lines.journal_id.id,
					'ref' : lines.name,
					'line_ids' : move_line,
					})
				jounral.action_post()


class RemainingEntriesLines(models.TransientModel):
	_name = "remain.entries.lines"
	_description = "Remaining Entries Lines"


	reccuring_payment_id = fields.Many2one('reccuring.payments')
	date = fields.Date(string="Start Date")
	name = fields.Char(string="Name")
	amount = fields.Float(string="Amount")
	credit_account_id =fields.Many2one('account.account')
	debit_account_id =fields.Many2one('account.account')
	journal_id = fields.Many2one('account.journal', string='Journal' ,required=True)
	generate_journal = fields.Selection([('posted', 'Posted'), ('unposted', 'Unposted')],
				string='Generate Journal',required=True)