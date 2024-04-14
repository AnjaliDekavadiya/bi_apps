# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

from odoo import api, fields, models, _
import logging 
_logger=logging.getLogger(__name__)


class MrpProduction(models.TransientModel):
    _name = "mrp.production.cancel.wizard"
    _description = "Showing wizard to cancel manufacturing order"

    reason = fields.Many2one('production.cancel.reason', 'Reason')
    comment = fields.Text('Comment')

    def cancel_order_button(self):
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        for obj in active_ids:
            productions = self.env['mrp.production'].browse(obj)
            if productions.state == 'done':
                unbuild=productions.button_unbuild()
                vals={'product_qty':productions.product_qty,'product_uom_id':productions.product_uom_id.id}
                if productions.lot_producing_id:
                    vals['lot_id']=productions.lot_producing_id.id
                unbuild_object=self.env['mrp.unbuild'].with_context(unbuild['context']).create(vals)
                unbuild_object.action_unbuild()
            productions._action_cancel_approve(self.reason, self.comment)
