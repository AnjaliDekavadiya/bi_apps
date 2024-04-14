# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
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

from odoo import models, _

class WebsiteMessageWizard(models.TransientModel):
    _inherit="website.message.wizard"

    def update_latest_record(self):
        active_model = self.env[self._context.get('active_model')]
        if self._context.get('active_model') == 'age.verification.config.settings':
            active_id = self._context.get('active_id') or self._context.get('active_ids')[0]
            active_record = active_model.browse(active_id)
            is_active_record = active_model.search([('is_active','=',True), ('website_id', '=', active_record.website_id.id)],limit=1)
            is_active_record.is_active = False
            active_record.is_active = True
        else:
            return super(WebsiteMessageWizard, self).update_latest_record()
        return True