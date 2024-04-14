# -*- coding: utf-8 -*-

from odoo import models, fields , api


class FleetRequest(models.Model):
    _inherit = "fleet.request"

    material_requisition_fleet_req_line_ids = fields.One2many(
        'material.requisition.fleet.req',
        'fleet_request_id',
        string='Materail Requisitions Fleet Request Lines',
        copy=True,
    )
    custom_material_requisition_ids = fields.Many2many(
        'material.purchase.requisition',
        string='Material Requisition Requests',
        readonly=True
    )
    requisition_count = fields.Integer(
        compute='_compute_requisition_counter',
        string="Requisition Count"
    )

    def _compute_requisition_counter(self):
        for rec in self:
            rec.requisition_count = self.env['material.purchase.requisition'].search_count([('custom_fleet_request_id','in', rec.ids)])

    # @api.multi
    def view_material_requisition(self):
        self.ensure_one()
        # for rec in self:
        # action = self.env.ref('material_purchase_requisitions.action_material_purchase_requisition').sudo().read()[0]
        action = self.env['ir.actions.actions']._for_xml_id('material_purchase_requisitions.action_material_purchase_requisition')
        action['domain'] = [('custom_fleet_request_id','=', self.id)]
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
