# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _

class FleetVehicleLogServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'
    _description = 'Services for vehicles'

    task_ids = fields.One2many(
        'project.task',
        'service_id',
        string="Task",
    )

    # @api.multi #odoo13
    def action_create_joborder(self):
        lines = []
        # for service in self.cost_ids:
        #     lines.append((4,service.cost_subtype_id.id))
        action = self.env.ref('fleet_job_work_orders.action_create_job_order_add').sudo().read()[0]
        action['context'] = {
            # 'default_name':self.cost_subtype_id.name,
            'default_newc_vehicle_id':self.vehicle_id.id,
            'default_newc_purchaser_id':self.purchaser_id.id,
            'default_newc_vendor_id':self.vendor_id.id,
            'default_newc_inv_ref':self.inv_ref,
            'default_newc_cost_ids':lines,
            'default_newc_odometer':self.odometer,
            'default_newc_odometer_unit':self.odometer_unit,
            'default_newc_notes':self.notes
        }
        return action

    # @api.multi #odoo13
    def action_view_task(self):
        self.ensure_one()
        action = self.env.ref('fleet_job_work_orders.action_project_all_task_job_order').sudo().read()[0]
        action['domain'] = str([('service_id', 'in', self.ids)])
        return action

class ProjectTask(models.Model):
    _inherit = "project.task"

    service_id = fields.Many2one(
        'fleet.vehicle.log.services',
        string="Fleet Service"
    )
    custom_vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string="Vehicle"
    )
    custom_purchaser_id = fields.Many2one(
        'res.partner',
        string="Purchase"
    )
    custom_vendor_id = fields.Many2one(
        'res.partner',
        string="Vendor"
    )
    inv_ref = fields.Char(
        string ='Invoice Reference'
    )
    custom_cost_ids = fields.Many2many(
        'fleet.service.type', 
        string="Included Services", 
    )
    odometer = fields.Float(
        string='Odometer',
        required=True
    )
    odometer_unit = fields.Selection([
        ('kilometers', 'Kilometers'),
        ('miles', 'Miles')
        ], 'Odometer Unit', default='kilometers',
        required=True
    )
    custom_is_service = fields.Boolean(
        string="Is Service Related?",
        copy= True,
    )

    # @api.multi #odoo13
    def action_view_service(self):
        self.ensure_one()
        action = self.env.ref('fleet.fleet_vehicle_log_services_action').sudo().read()[0]
        action['domain'] = str([('task_ids', 'in', self.ids)])
        return action
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: