# -*- coding: utf-8 -*-
##########################################################################
# 2010-2017 Webkul.
#
# NOTICE OF LICENSE
#
# All right is reserved,
# Please go through this link for complete license : https://store.webkul.com/license.html
#
# DISCLAIMER
#
# Do not edit or add to this file if you wish to upgrade this module to newer
# versions in the future. If you wish to customize this module for your
# needs please refer to https://store.webkul.com/customisation-guidelines/ for more information.
#
# @Author        : Webkul Software Pvt. Ltd. (<support@webkul.com>)
# @Copyright (c) : 2010-2017 Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# @License       : https://store.webkul.com/license.html
#
##########################################################################

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)

class MarketplaceRmaConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	mp_days_for_rma = fields.Integer(string="Seller Return Policy", help="Number of days upto which customer can request for RMA after delivery done.")
	mp_rma_day_apply_on = fields.Selection([("so_date", "Order Date"),("do_date", "Delivery Date")], string="Return Policy Apply On")
	enable_notify_seller_4_rma = fields.Boolean(string="Enable Notification Seller For RMA")
	notify_seller_for_rma_creation = fields.Many2one(
        "mail.template", string="Mail Template to Notify Seller On RMA Request", domain="[('model_id.model','=','rma.rma')]")

	def set_values(self):
		super(MarketplaceRmaConfigSettings, self).set_values()
		self.env['ir.default'].sudo().set('res.config.settings', 'mp_days_for_rma', self.mp_days_for_rma)
		self.env['ir.default'].sudo().set('res.config.settings', 'mp_rma_day_apply_on', self.mp_rma_day_apply_on)
		self.env['ir.default'].sudo().set('res.config.settings', 'enable_notify_seller_4_rma', self.enable_notify_seller_4_rma)
		self.env['ir.default'].sudo().set('res.config.settings', 'notify_seller_for_rma_creation', self.notify_seller_for_rma_creation.id)
		return True

	@api.model
	def get_values(self):
		res = super(MarketplaceRmaConfigSettings, self).get_values()
		mp_days_for_rma = self.env['ir.default'].sudo()._get('res.config.settings', 'mp_days_for_rma')
		mp_rma_day_apply_on = self.env['ir.default'].sudo()._get('res.config.settings', 'mp_rma_day_apply_on')
		enable_notify_seller_4_rma = self.env['ir.default'].sudo()._get('res.config.settings', 'enable_notify_seller_4_rma')
		notify_seller_for_rma_creation = self.env['ir.default'].sudo()._get('res.config.settings', 'notify_seller_for_rma_creation')
		res.update({"mp_days_for_rma" : mp_days_for_rma,
					"mp_rma_day_apply_on" : mp_rma_day_apply_on,
					"enable_notify_seller_4_rma" : enable_notify_seller_4_rma,
					"notify_seller_for_rma_creation" : notify_seller_for_rma_creation,})
		return res
