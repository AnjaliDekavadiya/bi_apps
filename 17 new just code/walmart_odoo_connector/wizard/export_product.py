# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2020-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
from odoo import models


class ExportProducts(models.TransientModel):
    _inherit = "export.products"

    def export_walmart_products(self):
        return self.env['export.operation'].create(
            {
                'channel_id': self.channel_id.id,
                'operation': self.operation,
            }
        ).export_button()
