# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
# from odoo.exceptions import Warning , UserError
from odoo.exceptions import UserError


class MaterialPurchaseRequisition(models.Model):
    _inherit = 'material.purchase.requisition'
    
    custom_currency_id = fields.Many2one(
        'res.currency', 
        string='Currency',
        default=lambda self: self.env.user.company_id.currency_id,
        readonly=True,
    )
    amount_total = fields.Float(
        string='Total Cost Price', 
        store=True, 
        readonly=True, 
        compute='_amount_all'
    )

    @api.depends('requisition_line_ids.total_cost_price')
    def _amount_all(self):
        for requisition in self:
            requisition.amount_total = sum(requisition.requisition_line_ids.mapped('total_cost_price'))

    # @api.multi #odoo13
    def requisition_confirm(self):
        for rec in self:
            if rec.amount_total > 0 and rec.employee_id.sudo().custom_purchase_requisition_limit > 0 and rec.amount_total >= rec.employee_id.sudo().custom_purchase_requisition_limit:
                # raise Warning("You are exeeding requisition limit so you can not confirm. please contact your manager.")
                raise UserError(_("You are exeeding requisition limit so you can not confirm. please contact your manager."))
            start_date = rec.request_date.replace(day=1)
            end_date = start_date + relativedelta(days=-1,months=+1)
            requisitions = self.env['material.purchase.requisition'].search([('employee_id', 'in', rec.employee_id.ids),('request_date','>=',start_date),('request_date','<=',end_date)])
            s_total = sum(requisitions.mapped('amount_total'))
            if s_total > 0 and rec.state not in ('cancel', 'reject') and rec.employee_id.sudo().custom_monthly_purchase_requisition_limit > 0 and s_total >= rec.employee_id.sudo().custom_monthly_purchase_requisition_limit:
                # raise Warning("You are exeeding monthly requisition limit so you can not confirm. please contact your manager.")
                raise UserError(_("You are exeeding monthly requisition limit so you can not confirm. please contact your manager."))
        return super(MaterialPurchaseRequisition, self).requisition_confirm()

    # @api.multi #odoo13
    def user_approve(self):
        for rec in self:
            if rec.amount_total > 0 and rec.employee_id.sudo().custom_purchase_requisition_limit > 0 and rec.amount_total >= rec.employee_id.sudo().custom_purchase_requisition_limit:
                # raise Warning("You are exeeding requisition limit so you can not confirm. please contact your manager.")
                raise UserError(_("You are exeeding requisition limit so you can not confirm. please contact your manager."))
            start_date = rec.request_date.replace(day=1)
            end_date = start_date + relativedelta(days=-1,months=+1)
            requisitions = self.env['material.purchase.requisition'].search([('employee_id', 'in', rec.employee_id.ids),('request_date','>=',start_date),('request_date','<=',end_date)])
            s_total = sum(requisitions.mapped('amount_total'))
            if s_total > 0 and rec.state not in ('cancel', 'reject') and rec.employee_id.sudo().custom_monthly_purchase_requisition_limit > 0 and s_total >= rec.employee_id.sudo().custom_monthly_purchase_requisition_limit:
                # raise Warning("You are exeeding monthly requisition limit so you can not confirm. please contact your manager.")
                raise UserError(_("You are exeeding monthly requisition limit so you can not confirm. please contact your manager."))
        return super(MaterialPurchaseRequisition, self).user_approve()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
