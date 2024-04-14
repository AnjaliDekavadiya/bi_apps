# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    company_branch_id = fields.Many2one(
        'res.company.branch',
        string="Branch",
        copy=False,
        tracking=True,
        default=lambda self: self.env.user.company_branch_id.id#odoo14
    )
    
#    @api.model odoo13
#    def create(self, vals):
#        context = dict(self._context or {})
#        if vals.get("stock_move_id"):
#            move_id = self.env['stock.move'].sudo().browse(int(vals.get("stock_move_id")))
#            vals.update({
#                'company_branch_id': move_id.company_branch_id.id
#            })
#            
#        if context.get('payment_branch_spl_custom'):
#            vals.update({
#                'company_branch_id': context.get('payment_branch_spl_custom')
#            })
#        return super(AccountMove, self).create(vals)
       
        
    @api.model_create_multi
    def create(self, vals_list):
        context = dict(self._context or {})
        for vals in vals_list:
            if vals.get("stock_move_id"):
                move_id = self.env['stock.move'].sudo().browse(int(vals.get("stock_move_id")))
                vals.update({
                    'company_branch_id': move_id.company_branch_id.id
                })
                
            if context.get('payment_branch_spl_custom'):
                vals.update({
                    'company_branch_id': context.get('payment_branch_spl_custom')
                })
        return super(AccountMove, self).create(vals_list)
        
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
