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
from odoo.exceptions import RedirectWarning
from odoo.exceptions import UserError
from odoo.addons.account.wizard.account_move_reversal import AccountMoveReversal
import odoo.osv.osv as osv

import datetime
import logging
_logger = logging.getLogger(__name__)


class AccountMoveReversal(AccountMoveReversal):
    _inherit = "account.move.reversal"

    @api.constrains('journal_id', 'move_ids')
    def _check_journal_type(self):
        context = dict(self._context or {})
        for record in self:
            if context.get("active_model") == "rma.rma" or context.get("active_model") == "rma.wizard":
                continue
            if record.journal_id.type not in record.move_ids.journal_id.mapped('type'):
                raise UserError(_('Journal should be the same type as the reversed entry.'))

    def reverse_moves(self):
        context = dict(self._context or {})
        if context.get("active_model") == "rma.rma"  or context.get("active_model") == "rma.wizard":
            rma_obj = self.env["rma.rma"].browse(context.get("params", {}).get("id", False) or context.get("id", False))

            if rma_obj:
                if not rma_obj.order_id.invoice_ids :
                    raise UserError('Invoice can not be refund because Order "' + rma_obj.order_id.name+ '" has no invoice.')
                if rma_obj.picking_id.state not in ['done'] :
                    raise UserError('Please validate incoming transfer first.')
                only_out_invoice_ids = []
                for inv in rma_obj.order_id.invoice_ids:
                    if inv.move_type == "out_invoice":
                        only_out_invoice_ids.append(inv.id)
                only_out_invoice_ids.sort()
                context["active_id"] = only_out_invoice_ids[0]
                context["active_ids"] = only_out_invoice_ids
                context["rma_id"] = rma_obj.id

        self.move_ids = self.env['account.move'].browse(self.env.context['active_ids']) if self.env.context.get('active_model') == 'rma.rma' else self.move_ids
        if not context.get("active_id"):
            raise osv.except_osv(_('Warning!'), _('Order %s has no invoice to refund.',(self.env["rma.rma"].browse(context.get("rma_id", False)))))
        return super(AccountMoveReversal, self.with_context(context)).reverse_moves()
