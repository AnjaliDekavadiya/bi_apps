# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class Company(models.Model):
	_inherit = 'res.company'

	consume_parts = fields.Boolean(string="Consume Parts from Stock", default=False)
	location_id = fields.Many2one('stock.location', string="Inventory Location")
	location_dest_id = fields.Many2one('stock.location', string="Consumed Part Location")

class ConsumePartsSetting(models.TransientModel):
	_inherit = 'res.config.settings'

	consume_parts = fields.Boolean(related='company_id.consume_parts',string="Consume Parts from Stock",readonly=False)
	location_id = fields.Many2one('stock.location',related='company_id.location_id',string="Inventory Location",readonly=False)
	location_dest_id = fields.Many2one('stock.location',related='company_id.location_dest_id',string="Consumed Part Location",readonly=False)

