# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
from odoo import fields, models


class ImportWizard(models.TransientModel):
	_inherit = 'channel.import'

	hubspot_filter = fields.Selection(
		selection=[
			('all','All'),
			# ('from','From ID'),
			('id','By ID'),
		],
		string='Hubspot Filter',
	)
	hubspot_id = fields.Char('Hubspot ID')

	def hubspot_get_filter(self):
		object_filter = self.hubspot_filter
		kw = {'object_filter': object_filter}
		if object_filter == 'id':
			kw['object_id'] = self.hubspot_id
		return kw
