# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
#See LICENSE file for full copyright and licensing details.

from odoo import models, fields , api

class CarRepair(models.Model):
    _inherit = "car.repair.support"

    material_requisition_car_repair_ids = fields.One2many(
        'material.requisition.car.repair',
        'requisition_id',
        string='Material Requisitions Car Repair',
        copy=False,
    )

    custom_material_requisition_ids = fields.Many2many(
        'material.purchase.requisition',
        string='Material Requisition Requests',
        readonly=True,
        copy=False,
    )

    requisition_count = fields.Integer(
        compute='_compute_requisition_counter',
        string="Requisition Count",
    )

    def _compute_requisition_counter(self):
        for rec in self:
            rec.requisition_count = self.env['material.purchase.requisition'].search_count([('custom_car_repair_id','in', rec.ids)])

    #@api.multi
    def action_material_requisition(self):
        self.ensure_one()
        # action = self.env.ref('car_repair_material_requisition.car_action_material_purchase_requisition').sudo().read()[0]
        action = self.env['ir.actions.actions']._for_xml_id('car_repair_material_requisition.car_action_material_purchase_requisition')
        # action['domain'] = [('custom_car_repair_id','in', self.ids)]
        action['domain'] = [('custom_car_repair_id','=', self.id)]
        return action


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
