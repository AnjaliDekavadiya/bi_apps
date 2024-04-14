# -*- coding: utf-8 -*-

from odoo import api, fields, models,_
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta



class ReccuringTemplates(models.Model):
	_name = "recurring.templates"
	_description = "Reccuring Templates"


	name = fields.Char(string="Name")
	pay_time = fields.Selection([('direct', 'Pay Direct'), ('later', 'Pay Later')],
				string='Pay Time',required=True)
	credit_account_id = fields.Many2one('account.account', string='Credit Account' ,required=True)
	debit_account_id = fields.Many2one('account.account', string='Debit Account' ,required=True)
	journal_id = fields.Many2one('account.journal', string='Journal' ,required=True)
	reccuring_period = fields.Selection([('days', 'Days'), ('weeks', 'Weeks'),
			('months', 'Months'), ('years', 'Years')],string='Reccuring Period',required=True)
	reccuring_interval = fields.Integer(string="Reccuring Interval")
	start_date=fields.Date(string="Start Date")
	scheduled_date=fields.Date(string="Next Scheduled Date" , compute="get_schedule_date")
	amount = fields.Float(string="Amount")
	generate_journal = fields.Selection([('posted', 'Posted'), ('unposted', 'Unposted')],
				string='Generate Journal',required=True)
	states = fields.Selection([('draft', 'Draft'),('running', 'Running')], 
				string='States', copy=False, index=True, default='draft')
	note = fields.Text(string='Notes')

	
	def get_schedule_date(self):
		for record in self:
			if record.reccuring_period == 'days':
				if record.start_date:
					record.scheduled_date = record.start_date + timedelta(days=record.reccuring_interval)

			if record.reccuring_period == 'weeks':
				if record.start_date:
					record.scheduled_date = record.start_date + timedelta(record.reccuring_interval*7)

			months = record.reccuring_interval
			if record.reccuring_period  == 'months':
				if record.start_date:
					record.scheduled_date = record.start_date + relativedelta(months=months)

			years = record.reccuring_interval
			if record.reccuring_period  == 'years':
				if record.start_date:
					record.scheduled_date = record.start_date + relativedelta(years=years)
