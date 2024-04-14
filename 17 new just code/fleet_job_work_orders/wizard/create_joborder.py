 # -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api, _

class CreateJobOrder(models.TransientModel):
    _name = "create.job.order"

    name = fields.Char(
        string="Task Title",
        required=True
    )
    custom_user_id = fields.Many2one(
            'res.users',
            string="Assigned to",
            required=True
    )
    custom_project_id = fields.Many2one(
        'project.project',
        string="Project"
    )
    newc_vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string="Vehicle",
        required=True
    )
    newc_purchaser_id = fields.Many2one(
        'res.partner',
        string="Purchase",
        required=True
    )
    newc_vendor_id = fields.Many2one(
        'res.partner',
        string="Vendor",
        required=True
    )
    newc_inv_ref = fields.Char(
        string ='Invoice Reference',
        required=True
    )
    newc_cost_ids = fields.Many2many(
        'fleet.service.type', 
        string="Included Services", 
    )
    newc_odometer = fields.Float(
        string='Odometer',
        required=True
    )
    newc_odometer_unit = fields.Selection([
        ('kilometers', 'Kilometers'),
        ('miles', 'Miles')
        ], 'Odometer Unit', default='kilometers',
        required=True
    )
    newc_notes = fields.Text(
        string="Description"
    )

    # @api.multi #odoo13
    def action_create_job_order(self):
        active_ids = self._context.get('active_ids')
        service_id = self.env['fleet.vehicle.log.services'].browse(self._context.get('active_ids'))
        for rec in self:
            lines = []
            for service in rec.newc_cost_ids:
                lines.append((4,service.id))
            task_id = self.env['project.task'].create({
                    'name': rec.name,
                    'service_id':service_id.id,
                    'date_deadline':service_id.date,
                    'description':service_id.notes,
                    # 'activity_user_id':rec.custom_user_id.id,
                    'user_ids': [(4, rec.custom_user_id.id)],
                    'project_id':rec.custom_project_id.id,
                    'custom_vehicle_id':rec.newc_vehicle_id.id,
                    'custom_purchaser_id':rec.newc_purchaser_id.id,
                    'custom_vendor_id':rec.newc_vendor_id.id,
                    'inv_ref':rec.newc_inv_ref,
                    'odometer':rec.newc_odometer,
                    'odometer_unit':rec.newc_odometer_unit,
                    'custom_cost_ids':lines,
                    'custom_is_service':True,
                })
        action = self.env.ref('fleet_job_work_orders.action_project_all_task_job_order').sudo().read()[0]
        action['domain'] = str([('id', '=', task_id.id)])
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: