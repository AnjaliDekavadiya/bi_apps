# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _action_done(self):
        from_webhook = self._context.get('from_webhook')
        for rec in self:
            if not from_webhook:
                rec.wk_pre_do_transfer()
            result = super(StockPicking, rec)._action_done()
            if not from_webhook:
                rec.wk_post_do_transfer(result)

    def wk_pre_do_transfer(self):
        if self.sale_id and self.picking_type_code == 'outgoing':
            mapping_ids = self.sudo().sale_id.channel_mapping_ids
            if mapping_ids and mapping_ids[0].channel_id.state == 'validate' and mapping_ids[0].channel_id.active:
                channel_id = mapping_ids[0].channel_id
                if hasattr(channel_id, '%s_pre_do_transfer' % channel_id.channel) and channel_id.sync_shipment and channel_id.state == 'validate':
                    getattr(channel_id, '%s_pre_do_transfer' % channel_id.channel)(self, mapping_ids)

    def wk_post_do_transfer(self, result):
        if self.sale_id and self.picking_type_code == 'outgoing':
            mapping_ids = self.sudo().sale_id.channel_mapping_ids
            if mapping_ids and mapping_ids[0].channel_id.state == 'validate' and mapping_ids[0].channel_id.active:
                channel_id = mapping_ids[0].channel_id
                if hasattr(channel_id, '%s_post_do_transfer' % channel_id.channel) and channel_id.sync_shipment and channel_id.state == 'validate':
                    getattr(channel_id, '%s_post_do_transfer' % channel_id.channel)(self, mapping_ids, result)
