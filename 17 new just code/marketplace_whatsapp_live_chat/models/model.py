# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)



class ResPartner(models.Model):
    _inherit = 'res.partner'

    allow_whatsapp_support = fields.Boolean(default=True)

    def mp_whatsapp_support_toggle(self):
        for rec in self:    
            rec.allow_whatsapp_support = not rec.allow_whatsapp_support
            if not rec.allow_whatsapp_support:
                rec.whatsapp_support_member = False
            
    
class Website(models.Model):
    _inherit = 'website'

    @api.model
    def check_seller(self,partner):
        if partner and partner.state == 'denied':
            return False
        return True

    def get_active_whatsapp_members(self):
        res = super(Website,self).get_active_whatsapp_members()
        if res:
            res = res.filtered(lambda r:self.check_seller(r)) 
        return res