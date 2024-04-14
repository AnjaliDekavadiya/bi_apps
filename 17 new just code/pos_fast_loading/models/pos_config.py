# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################

from odoo import models



class PosConfig(models.Model):
    _inherit = 'pos.config'

    def get_limited_products_loading(self, fields):
        mongo_server_rec = self.env['mongo.server.config'].search([('active_record','=',True)],limit=1)
        if mongo_server_rec and mongo_server_rec.cache_last_update_time and mongo_server_rec.is_pos_data_synced and (self._context.get('sync_from_mongo',False)):
            return self.env['product.product']._validate_product_data(fields, mongo_server_rec)
        else:
            pass
        return super().get_limited_products_loading(fields)