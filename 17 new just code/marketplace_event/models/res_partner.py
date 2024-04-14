# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    wk_event_seller_id = fields.Many2one('res.partner', string='Event Seller Id', default=lambda self: self.env.user.partner_id.id if self.env.user.partner_id and self.env.user.partner_id.seller else self.env['res.partner'], copy=False,)
    auto_event_approve = fields.Boolean(string="Auto Event Approve", default=lambda self: self.env[
                                          'ir.default']._get('res.config.settings', 'mp_auto_event_approve'), copy=False)
    parent_id = fields.Many2one('res.partner', string='Related Company', default=lambda self: self.env.user.partner_id.id if self.env.user.partner_id and self.env.user.partner_id.seller else self.env['res.partner'], index=True)

    @api.onchange("set_seller_wise_settings")
    def on_change_seller_wise_settings(self):
        if self.set_seller_wise_settings:
            # res = super(ResPartner,self).on_change_seller_wise_settings()
            vals = {}
            vals["auto_event_approve"] = self.env['ir.default']._get('res.config.settings', 'mp_auto_event_approve')
            self.update(vals)
