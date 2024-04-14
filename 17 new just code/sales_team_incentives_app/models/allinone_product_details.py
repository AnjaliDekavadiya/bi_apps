# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, timedelta
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime
import calendar



class CrmGoalDefination(models.Model):
	_name = 'crm.goal.defination'
	_description= 'Crm Goal Defination'

	name = fields.Char(string='Name',required=True)
	requirements = fields.Text('Requirements', help="Enter here the internal requirements'")
	active = fields.Boolean('Active', default=True)

class CrmGoalDetails(models.Model):
	_name = 'crm.goal.details'
	_description= 'Crm Goal Configuration'


	name = fields.Many2one('crm.goal.defination','Goal Defination')
	sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
	requirements = fields.Text('Requirements', help="Enter here the internal requirements'", store=True, compute="_compute_requirements")
	target_value = fields.Float('Target Value')
	suffix = fields.Char('Suffix',readonly=True,
		default='leads')
	curr_value = fields.Float('Current Value')
	crm_chal_id = fields.Many2one('crm.challenge','Crm Challenge')

	@api.depends('name')
	def _compute_requirements(self):
		for record in self:
			record.requirements = record.name.requirements



class CrmChallenge(models.Model):
	_name = 'crm.challenge'
	_description = "Crm Challenge"
	_rec_name = 'chal_name'

	crm_goals_ids = fields.One2many('crm.goals',
		'crm_goal_chal_id',string='Goals')
	crm_lost_id = fields.Many2one('crm.lost.reason',
		'For every Succeeding User',required=True)
	crm_goal_details_ids = fields.One2many('crm.goal.details',
		'crm_chal_id',string='Stages')
	crm_calc_ids = fields.One2many('crm.incen.calc',
		'crm_challenge_id',string='Calculation')
	chal_name = fields.Char('Challenge Name')
	assign_chal = fields.Many2many('res.users',
		string = 'Assign Challenge To')
	reward_boolean =fields.Boolean(
		'Reward as soon as every goal is reached')
	periodicity = fields.Selection([('non_rec','Non Recurring'),
			('daily','Daily'),
			('weekly','Weekly'),
			('monthly','Monthly'),
			('yearly','Yearly')],
			'Periodicity')

	disp_mode = fields.Selection([('indi','Individuals'),
			('leader','Leader Board(Group Ranking)')],
			'Display Mode')
	responsible_id = fields.Many2one('res.users',
		'Responsible')
	inc_calc = fields.Boolean(
		'Use in Incentive Calculation')
	start_date = fields.Date('Start Date')
	end_date = fields.Date('End Date')
	state = fields.Selection([('draft','Draft'),
			('progress','In Progress'),
			('done','Done')],
			'States',readonly=True,default='draft')


	def records_user(self):
		return {
			'type': 'ir.actions.act_window',
			'view_mode': 'tree',
			'res_model': 'res.users',
			'view_id': False,
			'target': 'new',
		}

	def start_challenge(self):
		for order in self:
			for result in order.assign_chal:
				domain = []
				for stage in order.crm_goal_details_ids:
					domain += ([('invoice_user_id','=',result.id),('state','=','posted')])
					if self.start_date and self.end_date:
						start_date = self.start_date
						end_date = self.end_date
						domain += [('invoice_date','>=',self.start_date),('invoice_date','<=',self.end_date)]
					if self.periodicity == 'daily':
						start_date = date.today()
						end_date = date.today()
						domain += [('invoice_date','>=',start_date),('invoice_date','<=',end_date)]
					if self.periodicity == 'weekly':
						today = date.today()
						start_date = today - timedelta(days=today.weekday())
						end_date = start_date + timedelta(days=6)
						domain += [('invoice_date','>=',start_date),('invoice_date','<=',end_date)]
					if self.periodicity == 'monthly':
						today = date.today()
						start_date = datetime.now().date().replace(month=today.month, day=1)
						end_date = datetime.now().date().replace(month=today.month, day=calendar.mdays[today.month])
						domain += [('invoice_date','>=',start_date),('invoice_date','<=',end_date)]
					if self.periodicity == 'yearly':
						start_date = datetime.now().date().replace(month=1, day=1)    
						end_date = datetime.now().date().replace(month=12, day=31)
						domain += [('invoice_date','>=',start_date),('invoice_date','<=',end_date)]
					invoice_id = self.env['account.move'].search(domain)
					amount = 0.0
					for invoice_ids in invoice_id:
						amount += invoice_ids.amount_total
					stage.curr_value = amount
					self.crm_goals_ids = [(0,0,{
						'to_reach':stage.target_value,
						'crm_user_id':result.id,
						'crm_goal_def_id':stage.name.id,
						'curr_value':amount,
						'start_date':start_date,
						'end_date':end_date
					})]			
			order.write({'state':'progress'})

	def refresh_challenge(self):
		for order in self:
			for result in order.assign_chal:
				for stage in order.crm_goal_details_ids:
					domain = ([('invoice_user_id','=',result.id),('state','=','posted')])
					if self.start_date and self.end_date:
						start_date = self.start_date
						end_date = self.end_date
						domain += [('invoice_date','>=',self.start_date),('invoice_date','<=',self.end_date)]
					if self.periodicity == 'daily':
						start_date = date.today()
						end_date = date.today()
						domain += [('invoice_date','>=',start_date),('invoice_date','<=',end_date)]
					if self.periodicity == 'weekly':
						today = date.today()
						start_date = today - timedelta(days=today.weekday())
						end_date = start_date + timedelta(days=6)
						domain += [('invoice_date','>=',start_date),('invoice_date','<=',end_date)]
					if self.periodicity == 'monthly':
						today = date.today()
						start_date = datetime.now().date().replace(month=today.month, day=1)
						end_date = datetime.now().date().replace(month=today.month, day=calendar.mdays[today.month])
						domain += [('invoice_date','>=',start_date),('invoice_date','<=',end_date)]
					if self.periodicity == 'yearly':
						start_date = datetime.now().date().replace(month=1, day=1)    
						end_date = datetime.now().date().replace(month=12, day=31)
						domain += [('invoice_date','>=',start_date),('invoice_date','<=',end_date)]
					invoice_id = self.env['account.move'].search(domain)
					amount = 0.0
					for invoice_ids in invoice_id:
						amount += invoice_ids.amount_total
					stage.curr_value = amount
					crm_goals_ids = self.env['crm.goals'].search([('crm_user_id','=',result.id),('id','in',self.crm_goals_ids.ids)])
					if crm_goals_ids:
						for crm_g in crm_goals_ids:
							crm_g.write({
								'start_date':start_date,
								'end_date':end_date,
								'curr_value':amount
							})

	def action_view_goals(self):
		return {
			'name':'Related Goals',
			'type': 'ir.actions.act_window',
			'view_mode': 'tree',
			'res_model': 'crm.goals',
			'domain':[('id', 'in', self.crm_goals_ids.ids)],
			'context':{'search_default_salesperson': 1,'search_default_customer':1},
			'view_id': False,
			'target': 'current',
		}

	def action_view_scheme(self):
		return {
			'name':'Related Scheme',
			'type': 'ir.actions.act_window',
			'view_mode': 'tree,form',
			'res_model': 'crm.incen.scheme',
			'view_id': False,
			'target': 'current',
		}



class CrmGoals(models.Model):
	_name = 'crm.goals'
	_description = "Crm Goals"
	_rec_name = 'crm_user_id'

	@api.depends('curr_value', 'to_reach')
	def _calculate_comp(self):
		for order in self:
			order.complete = (order.curr_value / order.to_reach) * 100

	crm_goal_chal_id = fields.Many2one('crm.challenge')
	crm_goal_def_id = fields.Many2one('crm.goal.defination',
		'Stage ID')
	crm_user_id = fields.Many2one('res.users',
		'User ID')
	crm_chal_id = fields.Many2one('crm.challenge','Challenge')
	start_date = fields.Date('Start Date')
	end_date = fields.Date('End Date')
	curr_value = fields.Float('Current Value')
	to_reach = fields.Float('To Reach')
	complete = fields.Float(compute='_calculate_comp',
		string='Completeness')
	goal_perf = fields.Text('Goal Performance',
		readonly=True)





class CrmIncentiveScheme(models.Model):
	_name = 'crm.incen.scheme'
	_description = "Crm Incentive Scheme"


	name = fields.Char('Name')
	active = fields.Boolean('Active')
	based_on = fields.Selection([('linear','Linear'),
			('tiered','Tiered Commission Plan')],
			'Based On')
	incen_calc_ids = fields.One2many('crm.incen.calc',
		'incen_scheme_id',string='Incen Calc Ids')
	incen_reward_ids = fields.One2many('crm.incen.reward',
		'crm_scheme_id',string='Reward IDs')

	def compute_incentive(self):
		challenge_id = self.env['crm.challenge'].browse(self._context.get('active_id'))
		print(challenge_id,'kkkk')
		list1 = []
		for stage in challenge_id.crm_goals_ids:
			incen_calc_ids = self.env['crm.incen.calc'].search([
				('salesperson_id','=',stage.crm_user_id.id),
				('start_date','=',challenge_id.start_date),
				('end_date','=',challenge_id.end_date),
				], limit=1)
			if incen_calc_ids:
				for record in incen_calc_ids:
					record.achieve = stage.curr_value
				list1.append(incen_calc_ids.id)
			if not incen_calc_ids:
				result = self.incen_calc_ids.create({
					'salesperson_id':stage.crm_user_id.id,
					'target':stage.to_reach,
					'achieve':stage.curr_value,
					'start_date':challenge_id.start_date,
					'end_date':challenge_id.end_date
					})
				list1.append(result.id)
		incentive_calc_ids = self.env['crm.incen.calc'].browse(list1)
		var = 0.00
		for orders in self.incen_reward_ids:
			var += orders.reward
		if challenge_id.inc_calc == True:
			for results in incentive_calc_ids:
				variable = 0.00
				for reward in self.incen_reward_ids:
					if self.based_on == 'linear':
						if reward.ttype == 'amt':
							if results.achieve_percent >= reward.achieve_percent:
								results.incentive = reward.reward
						else:
							if reward.ttype == 'percent':
								if results.achieve_percent >= reward.achieve_percent:
									results.incentive = (reward.reward/var)*100
					elif self.based_on == 'tiered':
						if reward.ttype == 'amt':
							if results.achieve_percent >= reward.achieve_percent:
								results.incentive += reward.reward
						else:
							if reward.ttype == 'percent':
								if results.achieve_percent >= reward.achieve_percent:
									variable += reward.reward
									results.incentive = (variable/var)*100
					else:
						raise ValidationError('Please choose the which Based On Method you would like to calculate')	
		return {
			'xml_id':'sales_team_incentives_app.crm_incen_calc_action_view',
			'name':'Related Calculation',
			'type': 'ir.actions.act_window',
			'view_mode': 'tree,form',
			'res_model': 'crm.incen.calc',
			'view_id': False,
			'domain':[('id', 'in', incentive_calc_ids.ids)],
			'target': 'current',
		}




class CrmIncentiveCalc(models.Model):
	_name = 'crm.incen.calc'
	_description = 'Crm Incentive Calc'
	_rec_name = 'salesperson_id'

	def _calculate_comp(self):
		for order in self:
			order.achieve_percent = (order.achieve / order.target) * 100

	crm_accounting_ids = fields.One2many('crm.accounting',
		'incen_calc_id',string='CRM Accounting Ids')
	incen_scheme_id = fields.Many2one('crm.incen.scheme',
		'Incentive Scheme')
	crm_challenge_id = fields.Many2one('crm.challenge',
		'CRM Challenge')
	salesperson_id = fields.Many2one('res.users','Salesperson')
	target = fields.Float('Target')
	achieve = fields.Float('Achievement')
	achieve_percent = fields.Float(compute='_calculate_comp',
		string ='Achievement %')

	incentive = fields.Float('Incentive')
	start_date = fields.Date('Start Date')
	end_date = fields.Date('End Date')
	state = fields.Selection([('not_paid','Not Paid'),
		('submit','Submitted To Accountant'),
		('paid','Paid')],
			'State',readonly=True,default='not_paid')

	def submit_accountant(self):
		self.crm_accounting_ids = [(0,0,{'salesperson_id':self.salesperson_id.id,
				'target':self.target,
				'achievement':self.achieve,
				'achieve_percent':self.achieve_percent,
				'incentive':self.incentive,
				'state':'submit'})]

		self.write({'state':'submit'})

class CrmIncentiveReward(models.Model):
	_name = 'crm.incen.reward'
	_description = 'Crm Incentive Reward'

	crm_scheme_id = fields.Many2one('crm.incen.scheme')
	achieve_percent = fields.Float('Achieve %')
	reward = fields.Float('Reward')
	ttype = fields.Selection([('amt','Amount'),
			('percent','Percentage')],
			'Type')

