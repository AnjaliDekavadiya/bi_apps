# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model_create_multi
    def create(self, vals_list):
        res = super(StockQuant, self).create(vals_list)
        us = self._context.get('uid')
        user_id = False
        if us:
            user_id = self.env['res.users'].sudo().browse(self._context.get('uid'))
        for rec in res:
            if rec.company_branch_id:
                pass
            elif user_id and user_id.company_branch_id:
                rec.company_branch_id = user_id.company_branch_id.id
            else:
                pass
        return res    
    
#    @api.multi odoo13
    def write(self, vals):
        result = super(StockQuant, self).write(vals)
        us = self._context.get('uid')
        user_id = False
        if us:
            user_id = self.env['res.users'].sudo().browse(self._context.get('uid'))
        for rec in self:
            if not rec.company_branch_id and user_id and user_id.company_branch_id:
                rec.company_branch_id = user_id.company_branch_id.id
        return result
    
    company_branch_id = fields.Many2one(
        'res.company.branch',
        string="Branch",
        copy=False,
        default=lambda self: self.env.user.company_branch_id.id,
    )
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
