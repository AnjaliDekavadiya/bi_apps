# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ClothRepairRequestWizard(models.TransientModel):
    _name = "cloth.repair.request.wizard"
    _description = "Cloth Repair Request Wizard"

    probc_repair_product_id = fields.Many2one(
        'product.product',
        string="Product to Repair",
    )
    probc_quantity = fields.Float(
        string="Repair Quantity",
        default="1.0"
    )
    probc_uom_id = fields.Many2one(
        'uom.uom',
        string="Unit of Measure",
    )
    probc_invoice_method = fields.Selection([
        ('none', 'No Invoice'),
        ('b4repair', 'Before Repair'),
        ('after_repair', 'After Repair')],
        string="Invoice Method",
        default='none',
    )
    probc_project_id = fields.Many2one(
        'project.project',
        string="Project"
    )
    probc_company_id = fields.Many2one(
        'res.company', 'Company',
        readonly=True, index=True,
        default=lambda self: self.env.company)
    probc_location_id = fields.Many2one(
        'stock.location',
        string="Location",
    )
    probc_request_type = fields.Selection([
        ('task', 'Create Task'),
        ('request', 'Create Repair Request'),
        ('task_and_request', 'Create Task And Repair Request')],
        string="Action to Apply",
        default='task_and_request',
    )

    @api.onchange('probc_company_id')
    def _onchange_probc_company_id(self):
        if self.probc_company_id:
            warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.probc_company_id.id)], limit=1)
            self.probc_location_id = warehouse.lot_stock_id
        else:
            self.probc_location_id = False

    def create_repair_request(self):
        model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        for rec in self:
            if active_id and model == 'cloth.request.details':
                record = self.env[model].browse(active_id)
                task_id = False
                if rec.probc_request_type == 'task' or rec.probc_request_type == 'task_and_request':
                    vals = {
                        'partner_id': record.partner_id.id,
                        'company_id': record.company_id.id,
                        'cloth_request_id': record.id,
                        'description': record.internal_note,
                        'name': record.name + ' - ' + 'Repair Request',
                        # 'activity_user_id': self.env.user.id,
                        'user_ids': [self.env.user.id],
                        'project_id': self.probc_project_id.id
                    }
                    task_id = self.env['project.task'].sudo().create(vals)

                if rec.probc_request_type == 'request' or rec.probc_request_type == 'task_and_request':
                    picking_type = self.env['stock.picking.type'].search([
                    ('code', '=', 'repair_operation'),
                    ('warehouse_id.company_id', '=', rec.probc_company_id.id),
                    ],limit=1) 
                    repair_vals = {
                        'product_id': rec.probc_repair_product_id.id,
                        'product_qty': rec.probc_quantity,
                        'product_uom': rec.probc_uom_id.id,
                        # 'invoice_method': rec.probc_invoice_method,
                        'cloth_request_id': record.id,
                        'location_id': rec.probc_location_id.id,
                        'picking_type_id':picking_type.id
                    }
                    if task_id:
                        repair_vals.update({
                            'probc_task_id': task_id.id,    
                        })
                    repair_request_id = self.env['repair.order'].sudo().create(repair_vals)
                    if task_id:
                        task_id.probc_repair_id = repair_request_id.id
                if rec.probc_request_type == 'task' and task_id:
                    # action = self.env.ref("project.action_view_all_task").sudo().read()[0]
                    action = self.env['ir.actions.actions']._for_xml_id('project.action_view_all_task')
                    task_ids = self.env['project.task'].search([('cloth_request_id', 'in', record.ids)])
                    action['domain'] = [('id', 'in', task_ids.ids)]
                else:
                    #action = self.env.ref("repair.action_repair_order_tree").sudo().read()[0]
                    action = self.env['ir.actions.actions']._for_xml_id('repair.action_repair_order_tree')
                    repair_ids = self.env['repair.order'].search([('cloth_request_id', 'in', record.ids)])
                    action['domain'] = [('id', 'in', repair_ids.ids)]
                return action
