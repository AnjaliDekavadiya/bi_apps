# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class StockMove(models.Model):
    _inherit = "stock.move"
    
    def _prepare_account_move_vals(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost):
        self.ensure_one()
        valuation_partner_id = self._get_partner_id_for_valuation_lines()

        material_actual_cost = self.env['mrp.bom.material.cost'].search([('mrp_pro_material_id.name','=',self.reference),('product_id','=',self.product_id.product_tmpl_id.id)])
        if material_actual_cost :
            unit_material_cost = material_actual_cost.total_actual_cost
            move_ids = self._prepare_account_move_line(qty, abs(unit_material_cost), credit_account_id, debit_account_id, svl_id, description)
        
        elif self.production_id :
            move_ids = self._prepare_account_move_line(qty, abs(self.production_id.total_actual_all_cost), credit_account_id, debit_account_id,svl_id, description)
            
        else : 
            move_ids = self._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id,svl_id, description)

        svl = self.env['stock.valuation.layer'].browse(svl_id)
        if self.env.context.get('force_period_date'):
            date = self.env.context.get('force_period_date')
        elif svl.account_move_line_id:
            date = svl.account_move_line_id.date
        else:
            date = fields.Date.context_today(self)

        return {
            'journal_id': journal_id,
            'line_ids': move_ids,
            'partner_id': valuation_partner_id,
            'date': date,
            'ref': description,
            'stock_move_id': self.id,
            'stock_valuation_layer_ids': [(6, None, [svl_id])],
            'move_type': 'entry',
            'is_storno': self.env.context.get('is_returned') and self.env.company.account_storno,
        }