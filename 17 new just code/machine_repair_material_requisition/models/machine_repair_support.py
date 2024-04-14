# -*- coding: utf-8 -*-

# from openerp import models, fields, api
from odoo import models, fields, api #odoo13


class MachineRepairSupport(models.Model):
    _inherit = 'machine.repair.support'

    material_requisition_ids = fields.One2many(
        'material.purchase.requisition',
        'machine_repair_id',
        readonly=True,
        string="Material Requisitions"
    )
    material_requisition_count = fields.Integer(
        compute="_material_requisition_count",
    )

    # @api.multi #odoo13
    @api.depends()
    def _material_requisition_count(self):
        for rec in self:
            rec.material_requisition_count = len(rec.material_requisition_ids.ids)

    # @api.multi #odoo13
    def show_material_requisition_ids(self):
        for rec in self:
            # res = self.env.ref('material_purchase_requisitions.action_material_purchase_requisition')
            # res = res.sudo().read()[0]
            res = self.env["ir.actions.actions"]._for_xml_id("material_purchase_requisitions.action_material_purchase_requisition")
            res['domain'] = str([('machine_repair_id', '=', rec.id)])
            res['context'] = {
                'default_machine_repair_id': rec.id,
                'default_analytic_account_id': self.analytic_account_id.id
            }
        return res

    def action_create_material_requisition(self):
        context = self.env.context.copy()
        context.update({
            'default_machine_repair_id': self.id,
            'default_analytic_account_id': self.analytic_account_id.id
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'material.purchase.requisition',
            'view_mode': 'form',
            'res_id': False,
            'target': 'current',
            'context': context,
            'flags': {
                'form': {
                    'action_buttons': True,
                    'options': {
                        'mode': 'create'
                    }
                }
            }
        }