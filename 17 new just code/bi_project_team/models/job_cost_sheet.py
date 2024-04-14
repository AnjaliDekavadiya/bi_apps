# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields,models,api,_
from datetime import datetime,timedelta,date

class CostSheettags(models.Model):	
	_name="cost.sheet.tags"
	_description="Cost Sheet Tags"

	name = fields.Char(string="name")
	proj_team_id = fields.Many2one('project.teams',string="Project Team")
	project_id = fields.Many2one('project.project',"Project")
	job_cost_sheet_ids = fields.Many2many('job.cost.sheet','tags','cost_sheet_tags','job_cost_sheet',string="Tags")

class JobCostSheetInherit(models.Model):
	_inherit="job.cost.sheet"

	project_team_id = fields.Many2one('project.teams',string="Project Team")
	cost_sheet_tags_ids = fields.Many2many('cost.sheet.tags','tags','job_cost_sheet','cost_sheet_tags',string="Tags")
	
	@api.onchange('project_id')
	def add_project_team(self):
		for rec in self:
			if rec.project_id:
				rec.write({'project_team_id':rec.project_id.project_team_id.id})