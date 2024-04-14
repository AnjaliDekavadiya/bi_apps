# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class ShowImage(models.TransientModel):
	_name="show.image.wizard"
	_description = 'Show image'
	img = fields.Binary(string="Drawing Image", attachment=True,readonly=True)
	name = fields.Char(string='Name',readonly=True)

	@api.model 
	def default_get(self, flds):
		res = super(ShowImage,self).default_get(flds)
		active = self.env['contract.drawings'].browse(self.env.context.get('active_id')) 
		res['img'] = active.drawing_img
		res['name'] = active.name
		return res