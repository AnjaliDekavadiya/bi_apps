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
from odoo import fields, models, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class PublishConfirmation(models.TransientModel):
    _name = 'wk.publish.group'

    def get_news_group_active_id(self):
        return self.env['website.loyalty.management'].browse(self._context.get('active_id'))

    wk_seller_credits = fields.Many2one('website.loyalty.management', string='Credits',default=get_news_group_active_id)

    def unpublish_group(self):
        wk_active_group = self.env["website.loyalty.management"].search([('mp_seller_id.id','=',self.wk_seller_credits.mp_seller_id.id),('status','=','approved'),('website_id.id','=',self.wk_seller_credits.website_id.id),('website_published','=',True)])
        if wk_active_group:
            wk_active_group.website_published = False
            self.wk_seller_credits.website_published = True

    def do_nothing(self):
        return False