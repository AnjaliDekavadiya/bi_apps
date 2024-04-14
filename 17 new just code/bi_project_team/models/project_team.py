# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields,models,api,_
from datetime import datetime,timedelta,date

class projectTeams(models.Model):
	_name = "project.teams"
	_description = "Project Teams"

	name = fields.Char(string ="Name")
	proj_manager_id = fields.Many2one('res.users',string="Project Manager")
	code = fields.Integer("Code")
	site_engineer_id = fields.Many2one('res.users',string="Site Engineer/Supervisor")
	team_members_ids = fields.One2many('team.members','proj_team_id',string="Team Members")
	security_guards_ids = fields.One2many('security.guards','proj_team_id',string="Security guards")
	store_officer_ids = fields.One2many('store.officer','proj_team_id',string="Store Officer")
	internal_notes = fields.Text("Internal Notes")

	_sql_constraints = [
			('code_uniq', 'unique (code)', _('The code must be unique !')),
		]

class TeamMembers(models.Model):
	_name = "team.members"
	_description= "Team Members"

	user_id = fields.Many2one('res.users',string="Name")
	login = fields.Char(string="Login")
	language = fields.Char(string = "Language")
	latest_connection = fields.Datetime(string="Latest Connection")
	proj_team_id = fields.Many2one('project.teams',string="Project Team")
	project_id = fields.Many2one('project.project',"Project")
	job_order_id = fields.Many2one('job.order',"Job Order")
	
	@api.onchange('user_id')
	def onc_name(self):
		self.login = self.user_id.login
		langs = self.env['res.lang'].sudo().search([("code", "=", self.user_id.lang)])
		self.language = langs.name
		self.latest_connection =self.user_id.login_date

class SecurityGuards(models.Model):
	_name = "security.guards"
	_description = "Security Guards"

	user_id = fields.Many2one('res.users',string="Name")
	login = fields.Char(string="Login")
	language = fields.Char(string = "Language")
	latest_connection = fields.Datetime(string="Latest Connection")
	proj_team_id = fields.Many2one('project.teams',string="Project Team")
	project_id = fields.Many2one('project.project',"Project")
	job_order_id = fields.Many2one('job.order',"Job Order")

	@api.onchange('user_id')
	def onc_name(self):
		self.login = self.user_id.login
		langs = self.env['res.lang'].sudo().search([("code", "=", self.user_id.lang)])
		self.language = langs.name
		self.latest_connection =self.user_id.login_date

class StoreOfficer(models.Model):
	_name = "store.officer"
	_description = "Store Officer"

	user_id = fields.Many2one('res.users',string="Name")
	login = fields.Char(string="Login")
	language = fields.Char(string = "Language")
	latest_connection = fields.Datetime(string="Latest Connection")
	proj_team_id = fields.Many2one('project.teams',string="Project Team")
	project_id = fields.Many2one('project.project',"Project")
	job_order_id = fields.Many2one('job.order',"Job Order")
	
	@api.onchange('user_id')
	def onc_name(self):
		self.login = self.user_id.login
		langs = self.env['res.lang'].sudo().search([("code", "=", self.user_id.lang)])
		self.language = langs.name
		self.latest_connection =self.user_id.login_date

class PorjectInherit(models.Model):
	_inherit="project.project"

	project_team_id = fields.Many2one('project.teams',string="Project Team")
	team_members_ids = fields.One2many('team.members','project_id',string="Team Members")
	security_guards_ids = fields.One2many('security.guards','project_id',string="Security guards")
	store_officer_ids = fields.One2many('store.officer','project_id',string="Store Officer")