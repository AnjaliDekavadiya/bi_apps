# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


class ResUsersInherit(models.Model):
	_inherit = 'res.partner'

	is_customer = fields.Boolean(string="Customer");
	is_vendor = fields.Boolean(string="Vendor");
