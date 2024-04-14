# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields,models,api,_
from datetime import datetime,timedelta,date

class JobOrderInherit(models.Model):
	_inherit="job.order"

	project_team_id = fields.Many2one('project.teams',string="Project Team")
	team_members_ids = fields.One2many('team.members','job_order_id',related="project_team_id.team_members_ids",string="Team Members")
	security_guards_ids = fields.One2many('security.guards','job_order_id',related="project_team_id.security_guards_ids",string="Security guards")
	store_officer_ids = fields.One2many('store.officer','job_order_id',related="project_team_id.store_officer_ids",string="Store Officer")
	site_engineer_id = fields.Many2one('res.users',string="Site Engineer/Supervisor")
	
	@api.onchange('project_team_id')
	def onc_team(self):
		self.site_engineer_id = self.project_team_id.site_engineer_id
		self.team_members_ids = self.project_team_id.team_members_ids
		self.store_officer_ids = self.project_team_id.store_officer_ids
		self.security_guards_ids = self.project_team_id.security_guards_ids

	@api.onchange('project_id')
	def add_project_team(self):
		for rec in self:
			if rec.project_id:
				rec.write({'project_team_id':rec.project_id.project_team_id.id})