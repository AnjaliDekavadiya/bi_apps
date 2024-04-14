# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

from collections import defaultdict

from odoo import api, fields, models, _
import logging
_logger=logging.getLogger(__name__)

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def action_cancel(self):
        ctx = dict(self.env.context or {})
        if not ctx.get('force_cancel', False):
            return {
                'name': _('Cancel Order'),
                'view_mode': 'form',
                'res_model': 'mrp.production.cancel.wizard',
                'view_id': self.env.ref('wk_cancel_manufacturing_orders.cancel_manufacturing_order_wizard_view').id,
                'type': 'ir.actions.act_window',
                'context': ctx,
                'target': 'new'
            }
        return super(MrpProduction, self).action_cancel()

    def _action_cancel_approve(self, reason, comment):
        _logger.info('============%r=====self=====',self)
        ctx = dict(self.env.context or {})
        ctx.update({
            'reason': reason.name,
            'comment': comment,
            'force_cancel': True,
        })
        for production in self:
            production.with_context(ctx).action_cancel()
            template = self.env.ref(
                'wk_cancel_manufacturing_orders.mail_template_cancel_manufacturing_order')
            if template:
                template.with_context(ctx).send_mail(self.id,force_send=True)
               

    def _action_cancel(self):
        ctx = dict(self.env.context or {})
        if self.env.user.has_group('wk_cancel_manufacturing_orders.group_cancel_manufacturing_order') and ctx.get('force_cancel', False):
            documents_by_production = {}
            for production in self:
                documents = defaultdict(list)
                for move_raw_id in self.move_raw_ids.filtered(lambda m: m.state not in ('cancel')):
                    iterate_key = self._get_document_iterate_key(move_raw_id)
                    if iterate_key:
                        document = self.env['stock.picking']._log_activity_get_documents({move_raw_id: (move_raw_id.product_uom_qty, 0)}, iterate_key, 'UP')
                        for key, value in document.items():
                            documents[key] += [value]
                if documents:
                    documents_by_production[production] = documents

            self.workorder_ids.unlink()
            finish_moves = self.move_finished_ids.filtered(lambda x: x.state not in ('cancel'))
            raw_moves = self.move_raw_ids.filtered(lambda x: x.state not in ('cancel'))
            (finish_moves | raw_moves)._action_cancel()
            picking_ids = self.picking_ids.filtered(lambda x: x.state not in ('cancel'))
            picking_ids.action_cancel()

            for production, documents in documents_by_production.items():
                filtered_documents = {}
                for (parent, responsible), rendering_context in documents.items():
                    if not parent or parent._name == 'stock.picking' and parent.state == 'cancel' or parent == production:
                        continue
                    filtered_documents[(parent, responsible)] = rendering_context
                production._log_manufacture_exception(filtered_documents, cancel=True)
            return True
        else:
            return super(MrpProduction, self)._action_cancel()
