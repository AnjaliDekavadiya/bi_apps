# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
# from odoo.exceptions import Warning , UserError
from odoo.exceptions import UserError


class ClothRequestMaterialRequisition(models.TransientModel):
    _name = 'cloth.request.details.material.requisition.wizard'
    _description = 'Cloth Request Material Requisition Wizard'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1),
        required=True,
        copy=True,
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        required=True,
        copy=True,
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        copy=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
        required=True,
        copy=True,
    )
    request_date = fields.Date(
        string='Requisition Date',
        default=fields.Date.today(),
        required=True,
    )
    requisiton_responsible_id = fields.Many2one(
        'hr.employee',
        string='Requisition Responsible',
        copy=True,
    )
    date_end = fields.Date(
        string='Requisition Deadline', 
        help='Last date for the product to be needed',
        copy=True,
    )

    def create_custom_material_requisition(self):
        vals_list = []
        context = dict(self._context or {})
        active_id = self.env['cloth.request.details'].browse(context.get('active_id', False))
        for line in active_id.material_requisition_product_ids:
            if not line.requisition_line_id:
                lines = (0,0,{
                    'product_id': line.product_id.id,
                    'description': line.description,
                    'qty': line.qty,
                    'uom': line.uom.id,
                    'requisition_type': line.requisition_type,
                    'custom_line_id': line.id,
                    })
                vals_list.append(lines)
        # action = self.env.ref('material_purchase_requisitions.action_material_purchase_requisition').sudo().read()[0]
        action = self.env['ir.actions.actions']._for_xml_id('material_purchase_requisitions.action_material_purchase_requisition')
        action['views'] = [(self.env.ref('material_purchase_requisitions.material_purchase_requisition_form_view').id, 'form')]
        action['context'] = {
            'default_employee_id' : self.employee_id.id,
            'default_department_id' : self.department_id.id,
            'default_analytic_account_id' : self.analytic_account_id.id,
            'default_requisiton_responsible_id' : self.requisiton_responsible_id.id,
            'default_company_id' : self.company_id.id,
            'default_request_date' : self.request_date,
            'default_date_end' : self.date_end,
            'default_requisition_line_ids': vals_list,
            'default_custom_cloth_request_id' : active_id.id,
        }
        return action


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
