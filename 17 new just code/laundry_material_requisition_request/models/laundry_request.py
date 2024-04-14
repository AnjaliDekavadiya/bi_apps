# -*- coding: utf-8 -*-

from odoo import models, fields , api


class LaundryBusinessService(models.Model):
    _inherit = "laundry.business.service.custom"

    material_requisition_product_ids = fields.One2many(
        'material.requisition.laundry.req',
        'laundry_request_id',
        string='Material Requisitions Laundry Request Lines',
        copy=True,
    )
    custom_requisition_line_ids = fields.One2many(
        'material.purchase.requisition',
        'custom_laundry_request_id',
        string='Material Requisitions',
        copy=False,
        readonly=True
    )
    custom_requisition_count = fields.Integer(
        compute='_compute_requisition_counter',
        string="Requisition Count"
    )

    def _compute_requisition_counter(self):
        for rec in self:
            rec.custom_requisition_count = self.env['material.purchase.requisition'].search_count([('custom_laundry_request_id','=', rec.id)])

    def view_material_requisition_custom(self):
        for rec in self:
            action = self.env.ref('material_purchase_requisitions.action_material_purchase_requisition').sudo().read()[0]
            action['domain'] = [('custom_laundry_request_id','=', rec.id)]
            return action

class ProjectTask(models.Model):
    _inherit = "project.task"

    material_requisition_product_ids = fields.One2many(
        'material.requisition.laundry.req',
        'workorder_request_id',
        string='Material Requisitions Maintenance Request Lines',
        copy=True,
    )
    custom_requisition_line_ids = fields.One2many(
        'material.purchase.requisition',
        'custom_workorder_request_id',
        string='Material Requisitions',
        copy=False,
        readonly=True
    )
    custom_requisition_count = fields.Integer(
        compute='_compute_requisition_counter',
        string="Requisition Count"
    )

    def _compute_requisition_counter(self):
        for rec in self:
            rec.custom_requisition_count = self.env['material.purchase.requisition'].search_count([('custom_workorder_request_id','=', rec.id)])

    def view_material_requisition_custom(self):
        for rec in self:
            action = self.env.ref('material_purchase_requisitions.action_material_purchase_requisition').sudo().read()[0]
            action['domain'] = [('custom_workorder_request_id','=', rec.id)]
            return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
