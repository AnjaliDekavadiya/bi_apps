# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class TransmittalSubmittalType(models.Model):
	_name = 'transmittal.submittal.type'
	_description = "Transmittal Submittal Type"

	name = fields.Char(string="Name")

class TransmittalSubmittalMedium(models.Model):
	_name = 'transmittal.submittal.medium'
	_description = "Transmittal Submittal Medium"

	name = fields.Char(string="Name")   

class Project(models.Model):
	_inherit = "project.project"

	count  =  fields.Integer('Transmittal Submittal Count', compute='_transmittal_count')
	def _transmittal_count(self):
		for project in self:
			cost_ids = self.env['transmittal.submittal'].search([('project_id','=',self.name)])
			project.count = len(cost_ids)

	def invoice_line_button(self):
		self.ensure_one()
		return {
			'name': 'Transmital/Submittals',
			'type': 'ir.actions.act_window',
			'view_mode': 'tree,form',
			'res_model': 'transmittal.submittal',
			'domain': [('project_id','=',self.name)],
		}

class JobOrder(models.Model):
	_inherit = "job.order"

	count  =  fields.Integer('Transmittal Submittal Count', compute='_get_transmittal_submittal_count_job')
	def _get_transmittal_submittal_count_job(self):
		for project in self:
			cost_ids = self.env['transmittal.submittal'].search([('job_order_id','=',self.name)])
			project.count = len(cost_ids)

	def job_order_button(self):
		self.ensure_one()
		return {
			'name': 'Transmital/Submittals',
			'type': 'ir.actions.act_window',
			'view_mode': 'tree,form',
			'res_model': 'transmittal.submittal',
			'domain': [('job_order_id','=',self.name)],
		}

