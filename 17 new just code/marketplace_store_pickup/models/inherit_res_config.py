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

from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class MarketplaceConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"


    def execute(self):
        for rec in self:
            if not rec.group_mp_shop_allow:
                raise UserError(_("Sorry! Marketplace seller store pickup module using shop features, So you can't disable seller shop features.\nIf you want to disable seller shop features then first you have to uninstall Marketplace seller store pickup module."))
        return super(MarketplaceConfigSettings, self).execute()
