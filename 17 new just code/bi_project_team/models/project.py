# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields,models,api,_
from datetime import datetime,timedelta,date

class PorjectInherit(models.Model):
	_inherit="project.project"

	project_team_id = fields.Many2one('project.teams',string="Project Team")
	team_members_ids = fields.One2many('team.members','project_id',related="project_team_id.team_members_ids",string="Team Members")
	security_guards_ids = fields.One2many('security.guards','project_id',related="project_team_id.security_guards_ids",string="Security guards")
	store_officer_ids = fields.One2many('store.officer','project_id',related="project_team_id.store_officer_ids",string="Store Officer")
	site_engineer_id = fields.Many2one('res.users',string="Site Engineer/Supervisor")
	type_of_construction = fields.Selection([('commercial','Commercial'), ('residential','Residential')], 'Type of Construction')
	cstmr_id = fields.Many2one('res.partner')
	street = fields.Char('street')
	street2 = fields.Char('street2')
	zip = fields.Char('zip')
	city = fields.Char('city')
	state_id = fields.Many2one('res.country.state',string="State")
	country_id = fields.Many2one('res.country',string="Country")

	@api.onchange('project_team_id')
	def onc_team(self):
		self.site_engineer_id = self.project_team_id.site_engineer_id
		self.user_id = self.project_team_id.proj_manager_id
		self.team_members_ids = self.project_team_id.team_members_ids
		self.store_officer_ids = self.project_team_id.store_officer_ids
		self.security_guards_ids = self.project_team_id.security_guards_ids

	@api.onchange('cstmr_id')
	def onchange_partner_id(self):
		self.street = self.cstmr_id.street
		self.street2 = self.cstmr_id.street2
		self.zip = self.cstmr_id.zip
		self.city = self.cstmr_id.city
		self.country_id = self.cstmr_id.country_id
		self.state_id = self.cstmr_id.state_id