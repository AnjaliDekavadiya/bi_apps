# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from contextlib import ExitStack, contextmanager
from odoo.exceptions import UserError, ValidationError
from datetime import date,datetime

class CrmAccounting(models.Model):
	_name = 'crm.accounting'
	_description = "Crm Accounting"
	_rec_name = 'salesperson_id'


	journal_id = fields.Many2one('account.journal',
		'Journal')
	debit = fields.Many2one('account.account',
		'Debit Account')
	credit = fields.Many2one('account.account',
		'Credit Account')
	incen_calc_id = fields.Many2one('crm.incen.calc',
		'CRM calculation')
	salesperson_id = fields.Many2one('res.users',
		'Salesperson')
	target = fields.Float('Target')
	achievement = fields.Float('Achievement')
	achieve_percent = fields.Float('Achievement %',
		readonly=True)
	incentive = fields.Float('Incentive')
	state = fields.Selection([('not_paid','Not Paid'),
		('submit','Submitted To Accountant'),
		('paid','Paid'),
		('reject','Rejected')],
			'State',readonly=True,default='not_paid')


	
	def write(self,values):

		if values.get('salesperson_id'):
			self.incen_calc_id.write({
				'salesperson_id':values.get('salesperson_id')})
		if values.get('target'):
			self.incen_calc_id.write({
				'target':values.get('target')})
		if values.get('achievement'):
			self.incen_calc_id.write({
				'achieve':values.get('achievement')})
		if values.get('incentive'):
			self.incen_calc_id.write({
				'incentive':values.get('incentive')})

		return super(CrmAccounting,self).write(values)

	def approve(self):
		if (self.journal_id and self.debit and self.credit):

			result = self.env['account.move'].create({
				'journal_id':self.journal_id.id
				})
			result.line_ids = [(0,0,{'account_id':self.debit.id,
				'debit':self.incentive,'name':'Incentive'})]
			result.line_ids = [(0,0,{'account_id':self.credit.id,
				'credit':self.incentive,'name':'Incentive'})]

			self.write({'state':'paid'})
			self.incen_calc_id.write({'state':'paid'})

		else:
			raise ValidationError('Please Edit and Select the Journal, Debit and Credit Fields.')

	def reject(self):
		self.write({'state':'reject'})

class AccountMoveInherit(models.Model):
	_inherit = 'account.move'


	@contextmanager
	def _check_balanced(self , container):

		container = {'records': self, 'self': self}
		with self._disable_recursion(container, 'check_move_validity', default=True, target=False) as disabled:
			yield
			if disabled:
				return
				
		moves = container['records'].filtered(lambda move: move.line_ids)
		if not moves:
			return

		self.env['account.move.line'].flush_model(['balance', 'currency_id', 'move_id'])
		self.env['account.move'].flush_model(['journal_id'])
		self._cr.execute('''
			WITH error_moves AS (
				SELECT line.move_id,
					   ROUND(SUM(line.balance), currency.decimal_places) balance
				  FROM account_move_line line
				  JOIN account_move move ON move.id = line.move_id
				  JOIN account_journal journal ON journal.id = move.journal_id
				  JOIN res_company company ON company.id = journal.company_id
				  JOIN res_currency currency ON currency.id = company.currency_id
				 WHERE line.move_id IN %s
			  GROUP BY line.move_id, currency.decimal_places
			)
			SELECT *
			  FROM error_moves
			 WHERE balance !=0
		''', [tuple(moves.ids)])

		query_res = self._cr.fetchall()