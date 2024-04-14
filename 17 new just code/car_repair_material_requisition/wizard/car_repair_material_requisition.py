# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
#See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
# from odoo.exceptions import Warning, UserError,ValidationError
from odoo.exceptions import UserError,ValidationError

class CarRepairMaterialRequisition(models.TransientModel):
    _name = 'car.repair.material.requisition.wizard'
    _description = 'car.repair.material.requisition.wizard'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1),
        required=True
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        required=True
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
        required=True
    )
    request_date = fields.Date(
        string='Requisition Date',
        default=fields.Date.today(),
        required=True,
    )
    requisiton_responsible_id = fields.Many2one(
        'hr.employee',
        string='Requisition Responsible'
    )
    date_end = fields.Date(
        string='Requisition Deadline', 
        help='Last date for the product to be needed'
    )

    #@api.multi
    def create_material_requisition(self):
        purchase_requisition = self.env['material.purchase.requisition']
        purchase_requisition_line = self.env['material.purchase.requisition.line']
        car_id = self.env['car.repair.support'].browse(self.env.context.get('active_id'))
        for rec in self:
            requisition_vals = {
                        'employee_id' : rec.employee_id.id,
                        'department_id' : rec.department_id.id,
                        'analytic_account_id' : rec.analytic_account_id.id,
                        'requisiton_responsible_id' : rec.requisiton_responsible_id.id,
                        'company_id' : rec.company_id.id,
                        'request_date' : rec.request_date,
                        'date_end' : rec.date_end,
            }
            if not car_id.material_requisition_car_repair_ids:
                raise ValidationError(_('Please create some requisition lines.'))
            if all(line.custom_requisition_line_id for line in car_id.material_requisition_car_repair_ids):
                raise ValidationError(_('All requisition lines are True.'))
            pr_id = purchase_requisition.create(requisition_vals)
            car_id.custom_material_requisition_ids = [(4,p.id) for p in pr_id]
            pr_id.custom_car_repair_id = car_id.id
            for line in car_id.material_requisition_car_repair_ids:
                if not line.custom_requisition_line_id:
                    requisition_line_vals = {
                        'requisition_type': line.requisition_type,
                        'product_id': line.product_id.id,
                        'description': line.description,
                        'qty': line.qty,
                        'uom': line.uom.id,
                        'requisition_id' : pr_id.id,
                    }
                    prl_ids = purchase_requisition_line.create(requisition_line_vals)
                    line.write({
                        'custom_requisition_line_id': prl_ids.id
                    })
        return car_id.action_material_requisition()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
