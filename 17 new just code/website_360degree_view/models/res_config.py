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

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class Website360ViewConfig(models.TransientModel):
    _name = 'website.360.view.config'
    _inherit = 'res.config.settings'
    _description = 'Website 360 view config'

    
    enable_360_view = fields.Boolean(
        string="Enable 360° view", help = "Enable 360° view of product on you website.", related = 'website_id.enable_360_view', readonly = False)



    
    
