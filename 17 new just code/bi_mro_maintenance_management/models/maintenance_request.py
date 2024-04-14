# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from datetime import datetime, timedelta, date


class MaintenanceReqInherit(models.Model):
    _inherit = 'maintenance.request'

    @api.depends('equipment_id')
    def dep_equipment(self):
        self.products_ids = None
        if self.equipment_id:

            checklist = []
            products = []
            for i in self.equipment_id.equi_checklist_ids:
                checklist.append(i.id)
            self.equi_checklist_ids = [(6, 0, checklist)]

            for i in self.equipment_id.products_ids:
                products.append((0, 0, {
                    'product_id': i.product_id.id,
                    'qty': i.qty,
                    'uom_id': i.uom_id.id,
                    'name': i.name,
                }))
            self.products_ids = products

    equi_checklist_ids = fields.One2many('maintenance.checklist', 'maintenance_req_id', compute='dep_equipment',
                                         store=True)
    products_ids = fields.One2many('products', 'maintenance_req_id', "Products", compute='dep_equipment', store=True)
    is_job_order = fields.Boolean("Is job order created?")
    is_material_requisition = fields.Boolean("Is material requisition created?")
    desti_location_id = fields.Many2one('stock.location', "Destination Location")
    employee_id = fields.Many2one('hr.employee', "Material Requisition Employee")
    job_order_id = fields.Many2one('job.order')
    maintenance_requisition_id = fields.Many2one('material.purchase.requisition')

    _sql_constraints = [
        ('code_uniq', 'unique (name)', _('The name must be unique !')),
    ]

    def action_view_job_order(self):
        self.ensure_one()
        return {
            'name': 'Job Orders',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'job.order',
            'domain': [('id', '=', self.job_order_id.id)],
        }

    def action_view_material_purchase_requisition(self):
        self.ensure_one()
        return {
            'name': 'Purchase Requisition',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'material.purchase.requisition',
            'domain': [('id', '=', self.maintenance_requisition_id.id)],
        }

    def create_job_order(self):
        job_order = self.env['job.order'].create({
            'name': self.name,
            'user_id': self.user_id.id,
        })
        self.job_order_id = job_order
        self.is_job_order = True

    def create_material_requisition(self):
        pro_line = []
        for line in self.products_ids:
            pro_id = self.env['product.product'].search([('name', '=', line.product_id.name)])
            for product in pro_id:
                pro_line.append((0, 0, {'product_id': product.id,
                                        'description': line.name,
                                        'uom_id': line.uom_id.id,
                                        'qty': line.qty,

                                        }))
        dep = self.env['hr.department'].search([])[0]
        res = self.env['material.purchase.requisition'].create({
            'employee_id': self.employee_id.id,
            'requisition_date': datetime.now(),
            'department_id': dep.id,
            'maintenance_request_id': self.id,
            'requisition_line_ids': pro_line,
            'reason_for_requisition': self.description,
            'desti_loc_id': self.desti_location_id.id,
        })

        self.maintenance_requisition_id = res
        self.is_material_requisition = True
        data = self.env['material.purchase.requisition'].search([('id', '=', res.id)])
        self.job_order_id.maintenance_requisition_ids = [(6, 0, data.ids)]


class MaterialPurchaseRequisitionInherit(models.Model):
    _inherit = 'material.purchase.requisition'

    maintenance_request_id = fields.Many2one('maintenance.request', "Maintenance Request")
    source_loc_id = fields.Many2one('stock.location', " Source Location")
    desti_loc_id = fields.Many2one('stock.location', " Destination Location")
    job_order_id = fields.Many2one('job.order')


class InheritJobOrder(models.Model):
    _inherit = "job.order"

    maintenance_request_id = fields.Many2one('maintenance.request')
    maintenance_requisition_ids = fields.One2many('material.purchase.requisition', 'job_order_id',
                                                  "Material Purchase Requisition")
