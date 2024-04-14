# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class GridsData(models.Model):
	_name = 'grid.data'
	_description = "Grids Data"

	name = fields.Char();
	check = fields.Boolean();
	url = fields.Char();
	color = fields.Char();
	icon = fields.Char();
	count = fields.Integer();
	placeholder_count = fields.Char();



