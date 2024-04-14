# -*- coding: utf-8 -*-

from odoo import models, fields , api

class CrmLead(models.Model):
    _inherit = "crm.lead"

    material_requisition_lead_line_ids = fields.One2many(
        'material.requisition.lead.line',
        'requisition_id',
        string='Materail Requisitions Lead Line',
        copy=True,
    )

    custom_material_requisition_ids = fields.Many2many(
        'material.purchase.requisition',
        string='Material Requisition Request',
        readonly=True
    )

    requisition_count = fields.Integer(
        compute='_compute_requisition_counter',
        string="Requisition Count"
    )

    def _compute_requisition_counter(self):
        for rec in self:
            rec.requisition_count = self.env['material.purchase.requisition'].search_count([('custom_crm_lead_id','in', rec.ids)])

    #@api.multi
    def view_material_requisition(self):
        for rec in self:
            action = self.env.ref('material_purchase_requisitions.action_material_purchase_requisition').sudo().read()[0]
            action['domain'] = [('custom_crm_lead_id','in', rec.ids)]
            return action


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
