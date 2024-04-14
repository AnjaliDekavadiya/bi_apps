# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime,date, timedelta
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

class StockMoveInherit(models.Model):
    _inherit = 'stock.move'

    move_date = fields.Date(string="Date")
    move_remark = fields.Char(string="Remarks")

    def _action_done(self,cancel_backorder=False):
        res = super(StockMoveInherit, self)._action_done()
       
        for move in res:
          move.write({'date': move.move_date or fields.Datetime.now()})
          line_m = move.mapped('move_line_ids')

          move_id = self.env['account.move'].search([('stock_move_id','=',self.id)])
          move_id.update({'date':move.move_date})

          for line in move.mapped('move_line_ids'):
              line.write({'date': move.move_date or fields.Datetime.now()})
            
        return res

    def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost):
        self.ensure_one()
        AccountMove = self.env['account.move'].with_context(default_journal_id=journal_id)

        move_lines = self._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, description)

        if move_lines:
            date = self.move_date or self._context.get('force_period_date', fields.Date.context_today(self))
            new_account_move = AccountMove.sudo().create({
                'journal_id': journal_id,
                'line_ids': move_lines,
                'date': date,
                'ref': description,
                'stock_move_id': self.id,
                'stock_valuation_layer_ids': [(6, None, [svl_id])],
                'type': 'entry',
            })
            new_account_move.post()


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    picking_remark = fields.Char(string="Remarks")

    def button_validate_custom(self):

        if self.picking_type_id.code in ('internal','incoming'):            

            view = self.env.ref('bi_internal_receipt_backdate.wizard_validate_internal_transfer_form_readonly')
            return {
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'wizard.validate.internal.transfer',
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                    'res_id': False,
                    'context': self.env.context,
                }

        else:

            return super(StockPickingInherit, self).button_validate()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: