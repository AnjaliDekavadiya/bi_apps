# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
import logging
_logger = logging.getLogger(__name__)


class Contractdrawing(models.Model):
	_name = 'contract.drawings'
	_description = 'Contract Drawing'

	name = fields.Char(string='Drawing Name')
	description = fields.Text(string='Description')
	drawing_img = fields.Binary(string="Drawing Image", attachment=True)
	job_order_id = fields.Many2one('job.order','Job Order')

class JobOorder(models.Model):
	_inherit = "job.order"

	contract_drawings_ids = fields.One2many('contract.drawings','job_order_id',string=' Contract Drawings')

	
