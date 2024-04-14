# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError, ValidationError


class LabourJobCost(models.Model):
    _inherit = "job.cost.line"

    actual_requisition_qty = fields.Float(string='Actual Requisition Quantity', compute="get_actual_requisition_qty")

    def get_actual_requisition_qty(self):
        for line in self:
            qty = 0
            requisition_line_ids = self.env['requisition.line'].search([('product_id', '=', line.product_id.id), (
            'requisition_id.state', 'not in', ['new', 'department_approval', 'ir_approve', 'cancel'])])
            for requisition in requisition_line_ids:
                if line.product_id.id == requisition.product_id.id:
                    if requisition.job_cost_sheet_id.id in [line.material_job_cost_sheet_id.id,
                                                            line.overhead_job_cost_sheet_id.id]:
                        if requisition.job_cost_sheet_id.id != False:
                            qty += requisition.qty
            line.actual_requisition_qty = qty


class MaterialPurchaseRequisition(models.Model):
    _inherit = "material.purchase.requisition"

    account_analytic_id = fields.Many2one('account.analytic.account', string="Analytic Account")
    analytic_id = fields.Many2one('account.analytic.line', string="Analytic Account")
    job_order_id = fields.Many2one('job.order', string="Job Order")
    construction_project_id = fields.Many2one('project.project', string="Construction Project")
    job_cost_sheet_id = fields.Many2one('job.cost.sheet', string="Job Cost Sheet", domain="[('stage','=','done')]")

    def create_picking_po(self):
        purchase_order_obj = self.env['purchase.order']
        purchase_order_line_obj = self.env['purchase.order.line']
        for requisition in self:
            for line in requisition.requisition_line_ids:
                if line.requisition_action == 'purchase_order':
                    for vendor in line.vendor_id:
                        pur_order = purchase_order_obj.search(
                            [('requisition_po_id', '=', requisition.id), ('partner_id', '=', vendor.id)])
                        if pur_order:
                            po_line_vals = {
                                'product_id': line.product_id.id,
                                'product_qty': line.qty,
                                'name': line.description,
                                'price_unit': line.product_id.list_price,
                                'date_planned': datetime.now(),
                                'product_uom': line.uom_id.id,
                                'order_id': pur_order.id,
                            }
                            purchase_order_line = purchase_order_line_obj.create(po_line_vals)
                        else:
                            vals = {
                                'partner_id': vendor.id,
                                'date_order': datetime.now(),
                                'requisition_po_id': requisition.id,
                                'origin': requisition.sequence,
                                'job_id': requisition.job_order_id.id,
                                'project_id': requisition.construction_project_id.id,
                                'state': 'draft',
                                'picking_type_id': requisition.picking_type_id.id
                            }
                            purchase_order = purchase_order_obj.create(vals)
                            po_line_vals = {
                                'product_id': line.product_id.id,
                                'product_qty': line.qty,
                                'name': line.description,
                                'price_unit': line.product_id.list_price,
                                'date_planned': datetime.now(),
                                'product_uom': line.uom_id.id,
                                'order_id': purchase_order.id,
                            }
                            purchase_order_line = purchase_order_line_obj.create(po_line_vals)
                else:
                    stock_picking_obj = self.env['stock.picking']
                    stock_move_obj = self.env['stock.move']
                    stock_picking_type_obj = self.env['stock.picking.type']
                    picking_type_id = False

                    if not requisition.use_manual_locations:
                        picking_type_id = requisition.internal_picking_id
                    else:
                        picking_type_id = stock_picking_type_obj.search(
                            [('code', '=', 'internal'), ('company_id', '=', requisition.company_id.id or False)],
                            order="id desc", limit=1)

                    if line.vendor_id:
                        for vendor in line.vendor_id:

                            pur_order = stock_picking_obj.search(
                                [('requisition_picking_id', '=', requisition.id), ('partner_id', '=', vendor.id)])

                            if pur_order:
                                if requisition.use_manual_locations:
                                    pic_line_val = {
                                        'name': line.product_id.name,
                                        'product_id': line.product_id.id,
                                        'product_uom_qty': line.qty,
                                        'picking_id': picking_type_id.id,
                                        'product_uom': line.uom_id.id,
                                        'location_id': requisition.source_location_id.id,
                                        'location_dest_id': requisition.destination_location_id.id,
                                    }
                                else:
                                    pic_line_val = {
                                        'name': line.product_id.name,
                                        'product_id': line.product_id.id,
                                        'product_uom_qty': line.qty,
                                        'picking_id': picking_type_id.id,
                                        'product_uom': line.uom_id.id,
                                        'location_id': picking_type_id.default_location_src_id.id,
                                        'location_dest_id': picking_type_id.default_location_dest_id.id,
                                    }

                                stock_move = stock_move_obj.create(pic_line_val)
                            else:
                                if requisition.use_manual_locations:
                                    val = {
                                        'partner_id': vendor.id,
                                        'location_id': requisition.source_location_id.id,
                                        'location_dest_id': requisition.destination_location_id.id,
                                        'picking_type_id': picking_type_id.id,
                                        'material_requisition_id': requisition.job_order_id.id,
                                        'construction_project_id': requisition.construction_project_id.id,
                                        'analytic_account_id': requisition.analytic_id.id,
                                        'company_id': requisition.env.user.company_id.id,
                                        'requisition_picking_id': requisition.id,
                                        'origin': requisition.sequence
                                    }
                                else:
                                    val = {
                                        'partner_id': vendor.id,
                                        'location_id': picking_type_id.default_location_src_id.id,
                                        'location_dest_id': picking_type_id.default_location_src_id.id,
                                        'picking_type_id': picking_type_id.id,
                                        'material_requisition_id': requisition.job_order_id.id,
                                        'construction_project_id': requisition.construction_project_id.id,
                                        'analytic_account_id': requisition.analytic_id.id,
                                        'company_id': requisition.env.user.company_id.id,
                                        'requisition_picking_id': requisition.id,
                                        'origin': requisition.sequence
                                    }

                                stock_picking = stock_picking_obj.create(val)
                                if requisition.use_manual_locations:
                                    pic_line_val = {
                                        'partner_id': vendor.id,
                                        'name': line.product_id.name,
                                        'product_id': line.product_id.id,
                                        'product_uom_qty': line.qty,
                                        'product_uom': line.uom_id.id,
                                        'location_id': requisition.source_location_id.id,
                                        'location_dest_id': requisition.destination_location_id.id,
                                        'picking_id': stock_picking.id,
                                        'origin': requisition.sequence

                                    }
                                else:
                                    pic_line_val = {
                                        'partner_id': vendor.id,
                                        'name': line.product_id.name,
                                        'product_id': line.product_id.id,
                                        'product_uom_qty': line.qty,
                                        'product_uom': line.uom_id.id,
                                        'location_id': picking_type_id.default_location_src_id.id,
                                        'location_dest_id': picking_type_id.default_location_dest_id.id,
                                        'picking_id': stock_picking.id,
                                        'origin': requisition.sequence

                                    }
                                stock_move = stock_move_obj.create(pic_line_val)
                    else:
                        pur_order = stock_picking_obj.search([('requisition_picking_id', '=', requisition.id)])
                        if pur_order:
                            if requisition.use_manual_locations:
                                pic_line_val = {
                                    'name': line.product_id.name,
                                    'product_id': line.product_id.id,
                                    'product_uom_qty': line.qty,
                                    'picking_id': stock_picking.id,
                                    'product_uom': line.uom_id.id,
                                    'location_id': requisition.source_location_id.id,
                                    'location_dest_id': requisition.destination_location_id.id,
                                }
                            else:
                                pic_line_val = {
                                    'name': line.product_id.name,
                                    'product_id': line.product_id.id,
                                    'product_uom_qty': line.qty,
                                    'picking_id': stock_picking.id,
                                    'product_uom': line.uom_id.id,
                                    'location_id': picking_type_id.default_location_src_id.id,
                                    'location_dest_id': picking_type_id.default_location_dest_id.id,
                                }
                            stock_move = stock_move_obj.create(pic_line_val)
                        else:
                            if requisition.use_manual_locations:
                                val = {
                                    'picking_type_id': picking_type_id.id,
                                    'location_id': requisition.source_location_id.id,
                                    'location_dest_id': requisition.destination_location_id.id,
                                    'company_id': requisition.env.user.company_id.id,
                                    'material_requisition_id': requisition.job_order_id.id,
                                    'construction_project_id': requisition.construction_project_id.id,
                                    'analytic_account_id': requisition.analytic_id.id,
                                    'requisition_picking_id': requisition.id,
                                    'origin': requisition.sequence
                                }
                            else:
                                val = {
                                    'location_id': picking_type_id.default_location_src_id.id,
                                    'location_dest_id': picking_type_id.default_location_dest_id.id,
                                    'picking_type_id': picking_type_id.id,
                                    'material_requisition_id': requisition.job_order_id.id,
                                    'construction_project_id': requisition.construction_project_id.id,
                                    'analytic_account_id': requisition.analytic_id.id,
                                    'company_id': requisition.env.user.company_id.id,
                                    'requisition_picking_id': requisition.id,
                                    'origin': requisition.sequence
                                }

                            stock_picking = stock_picking_obj.create(val)
                            if requisition.use_manual_locations:
                                pic_line_val = {
                                    'name': line.product_id.name,
                                    'product_id': line.product_id.id,
                                    'product_uom_qty': line.qty,
                                    'product_uom': line.uom_id.id,
                                    'location_id': requisition.source_location_id.id,
                                    'location_dest_id': requisition.destination_location_id.id,
                                    'picking_id': stock_picking.id,
                                    'origin': requisition.sequence
                                }
                            else:
                                pic_line_val = {
                                    'name': line.product_id.name,
                                    'product_id': line.product_id.id,
                                    'product_uom_qty': line.qty,
                                    'product_uom': line.uom_id.id,
                                    'location_id': picking_type_id.default_location_src_id.id,
                                    'location_dest_id': picking_type_id.default_location_dest_id.id,
                                    'picking_id': stock_picking.id,
                                    'origin': requisition.sequence
                                }
                            stock_move = stock_move_obj.create(pic_line_val)
            requisition.write({
                'state': 'po_created',
            })


class RequisitionLine(models.Model):
    _inherit = "requisition.line"

    job_cost_sheet_id = fields.Many2one('job.cost.sheet', string="Job Cost Center",
                                        related="requisition_id.job_cost_sheet_id")


class JobCostSheet(models.Model):
    _inherit = 'job.cost.sheet'

    material_pur_req_count = fields.Integer('Material Purchase Requisition', compute='_get_material_pur_req_count')

    def unlink(self):
        for jcs in self:
            if jcs.material_pur_req_count > 0:
                raise UserError(_('Sorry !!! \n'
                                  'You cannot delete a job cost sheet if material purchase requisition is created'))

        return super(JobCostSheet, self).unlink()

    def _get_material_pur_req_count(self):
        for requisition_line in self:
            requisition_line_ids = self.env['material.purchase.requisition'].search(
                [('job_cost_sheet_id', '=', requisition_line.id)])
            requisition_line.material_pur_req_count = len(requisition_line_ids)

    def requisition_button(self):
        self.ensure_one()
        return {
            'name': 'Purchase Requisition',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'material.purchase.requisition',
            'domain': [('job_cost_sheet_id', '=', self.id)],
        }


class doc_generate(models.TransientModel):
    _name = 'purchase.requisitions.details'
    _description = "purchase requisitions details"

    job_cost_sheet_id = fields.Many2one('job.cost.sheet', string="Cost Sheet")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    department_id = fields.Many2one('hr.department', string="Department")
    vendor_id = fields.Many2many('res.partner', string="Vendor")

    @api.model
    def default_get(self, flds):
        result = super(doc_generate, self).default_get(flds)
        cost_id = self.env['job.cost.sheet'].browse(self._context.get('active_id'))
        result['job_cost_sheet_id'] = cost_id.id
        return result

    def create_purchase_req(self):
        cost_id = self.env['job.cost.sheet'].browse(self._context.get('active_id'))
        mater_pur = self.env['material.purchase.requisition']
        req_line_id = self.env['requisition.line']
        vals_line = []
        if self.job_cost_sheet_id:
            for material in self.job_cost_sheet_id.material_job_cost_line_ids:
                vals = {
                    'product_id': material.product_id.id,
                    'description': material.product_id.name,
                    'qty': material.quantity,
                    'job_cost_sheet_id': self.job_cost_sheet_id.id,
                    'uom_id': material.uom_id.id,
                    'vendor_id': [(6, 0, self.vendor_id.ids)]
                }
                vals_line.append((0, 0, vals))
            for overhead in self.job_cost_sheet_id.overhead_job_cost_line_ids:
                vals = {
                    'product_id': overhead.product_id.id,
                    'description': overhead.product_id.name,
                    'qty': overhead.quantity,
                    'uom_id': overhead.uom_id.id,
                    'job_cost_sheet_id': self.job_cost_sheet_id.id,
                    'vendor_id': [(6, 0, self.vendor_id.ids)]
                }
                vals_line.append((0, 0, vals))
        mater_pur.create({
            'employee_id': self.employee_id.id,
            'department_id': self.department_id.id,
            'job_cost_sheet_id': self.job_cost_sheet_id.id,
            'job_order_id': self.job_cost_sheet_id.job_order_id.id,
            'construction_project_id': self.job_cost_sheet_id.project_id.id,
            'analytic_id': self.job_cost_sheet_id.analytic_ids.id,
            'requisition_line_ids': vals_line
        })
        return


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model_create_multi
    def create(self, vals_list):
        res = super(StockPicking, self).create(vals_list)
        for line in res:
            purchase_order = self.env['purchase.order'].search([('name', '=', res.origin)], limit=1)
            if purchase_order.requisition_po_id:
                vals = {'material_requisition_id': purchase_order.requisition_po_id.job_order_id.id,
                        'job_order_user_id': purchase_order.requisition_po_id.requisition_responsible_id.id,
                        'construction_project_id': purchase_order.requisition_po_id.construction_project_id.id,
                        'analytic_account_id': purchase_order.requisition_po_id.analytic_id.id}
                res.write(vals)
        return res
