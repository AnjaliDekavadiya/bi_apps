# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError

class ClothRequestDetails(models.Model):
    _inherit = 'cloth.request.details'

    mrp_product_id = fields.Many2one(
        'product.product',
        string="Product (Cloth)"
    )
    custom_mrp_bom_line_ids = fields.One2many(
        'custom.mrp.bom.line',
        'custom_cloth_request_id',
        string="Bom Line"
    )
    custom_is_created_bom = fields.Boolean(
        string="Is Created BOM"
    )
    custom_bom_id = fields.Many2one(
        'mrp.bom',
        string="BOM"
    )
    custom_is_manufacturing_order = fields.Boolean(
        string="Is Created Manufacturing Order",
        copy=False
    )
    custom_bom_type = fields.Selection([
        ('new_bom', 'Create BOM'),
        ('old_bom', 'Use Existing BOM')],
        string="BOM Selection",
        default='old_bom'
    )

    def custom_action_mrp_work_orders(self):
        self.ensure_one()
        # action = self.env.ref('mrp.mrp_workorder_todo').sudo().read()[0]
        action = self.env['ir.actions.actions']._for_xml_id('mrp.mrp_workorder_todo')
        action['context'] = {}
        manufacturing_ids = self.env['mrp.production'].search([('custom_tailor_request_id', 'in', self.ids)])
        workorder_ids = self.env['mrp.workorder'].search([('production_id', 'in', manufacturing_ids.ids)])
        action['domain'] = [('id', 'in', workorder_ids.ids)]
        return action

    def custom_action_view_mrp_production(self):
        self.ensure_one()
        # action = self.env.ref('mrp.mrp_production_action').sudo().read()[0]
        action = self.env['ir.actions.actions']._for_xml_id('mrp.mrp_production_action')
        action['context'] = {}
        manufacturing_ids = self.env['mrp.production'].search([('custom_tailor_request_id', 'in', self.ids)])
        action['domain'] = [('id', 'in', manufacturing_ids.ids)]
        return action

    def action_custom_create_bom(self):
        for rec in self:
            if not rec.mrp_product_id:
                raise UserError(_("Please select product."))
            vals = {
                'product_tmpl_id': rec.mrp_product_id.product_tmpl_id.id,
                'product_id': rec.mrp_product_id.id,
                'product_qty': rec.quantity,
                'product_uom_id': rec.uom_id.id,
            }
            bom_id = self.env['mrp.bom'].create(vals)
            rec.custom_bom_id = bom_id.id
            if rec.custom_mrp_bom_line_ids and bom_id:
                for line in rec.custom_mrp_bom_line_ids:
                    line_vals = {
                        'product_id': line.custom_product_id.id,
                        'product_qty': line.custom_product_qty,
                        'product_uom_id': line.custom_product_uom_id.id,
                        'bom_id': bom_id.id,
                    }
                    self.env['mrp.bom.line'].create(line_vals)
            # action = self.env.ref('mrp.mrp_bom_form_action').sudo().read()[0]
            action = self.env['ir.actions.actions']._for_xml_id('mrp.mrp_bom_form_action')
            action['views'] = [(self.env.ref('mrp.mrp_bom_form_view').id, 'form')]
            action['context'] = {}
            if bom_id:
                action['res_id'] = bom_id.id
            else:
                action = {'type': 'ir.actions.act_window_close'}
            rec.custom_is_created_bom = True
            return action

    def action_custom_create_manufacturing_orders(self):
        for rec in self:
            if not rec.mrp_product_id:
                raise UserError(_("Please select product."))
            if not rec.custom_bom_id:
                raise UserError(_("Please select bom."))
            # action = self.env.ref('mrp.mrp_production_action').sudo().read()[0]
            action = self.env['ir.actions.actions']._for_xml_id('mrp.mrp_production_action')
            action['views'] = [(self.env.ref('mrp.mrp_production_form_view').id, 'form')]
            action['context'] = {
                'default_product_id': rec.mrp_product_id.id,
                'default_bom_id': rec.custom_bom_id.id,
                'default_custom_tailor_request_id': rec.id,
            }
            rec.custom_is_manufacturing_order = True
            return action


class CustomMrpBomLine(models.Model):
    _name = 'custom.mrp.bom.line'
    _description = "Mrp Bom Line"

    custom_product_id = fields.Many2one(
        'product.product',
        string="Material"
    )
    custom_product_qty = fields.Float(
        string="Quantity"
    )
    custom_product_uom_id = fields.Many2one(
        'uom.uom',
        string="Product Unit of Measure"
    )
    custom_cloth_request_id = fields.Many2one(
        'cloth.request.details',
        string="Cloth Request"
    )

    @api.onchange('custom_product_id')
    def onchange_custom_product_id(self):
        if self.custom_product_id:
            self.custom_product_uom_id = self.custom_product_id.uom_id.id