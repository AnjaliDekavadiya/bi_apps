# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MaintenanceEquipmentWizard(models.TransientModel):
    _name = 'maintenance.equipment.wizard'
    _description = 'Maintenance Equipment Wizard'

    name = fields.Char('Equipment Name', required=True)

    category_id = fields.Many2one(
        'maintenance.equipment.category',
        string='Equipment Category',
    )
    maintenance_team_id = fields.Many2one(
        'maintenance.team',
        string='Maintenance Team'
    )
    assign_date = fields.Date(
        'Assigned Date',
    )
    technician_user_id = fields.Many2one(
        'res.users',
        string='Technician',
    )
    location = fields.Char(
        'Location'
    )
    model = fields.Char(
        'Model'
    )
    serial_no = fields.Char(
        'Serial Number',
        copy=False
    )
    period = fields.Integer(
        'Days between each preventive maintenance'
    )
    maintenance_duration = fields.Float(
        help="Maintenance Duration in hours."
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id
    )
    note = fields.Text(
        'Note'
    )

    #@api.multi
    def create_maintenance_equipment(self):
        maintenance_equipment = self.env['maintenance.equipment']
        machine_id = self.env['machine.repair.support'].browse(int(self.env.context.get('active_id')))
        for rec in self:
            equipment_vals = {
                        'name': rec.name,
                        'category_id': rec.category_id.id,
                        'maintenance_team_id': rec.maintenance_team_id.id,
                        'assign_date': rec.assign_date,
                        'location': rec.location,
                        'model': rec.model,
                        'serial_no': rec.serial_no,
                        # 'period': rec.period,  #remove in odoo17
                        # 'maintenance_duration': rec.maintenance_duration,#remove in odoo17
                        'technician_user_id': rec.technician_user_id.id,
                        'company_id': rec.company_id.id,
                        'note': rec.note,
                        'custom_partner_id': machine_id.partner_id.id,
            }
            me_id = maintenance_equipment.create(equipment_vals)
            machine_id.write({
                        'custom_equipment_id': me_id.id,
                    })
        # action = self.env.ref('maintenance.hr_equipment_action').sudo().read()[0]
        action = self.env["ir.actions.actions"]._for_xml_id("maintenance.hr_equipment_action")
        action['domain'] = [('id', 'in', me_id.ids)]
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
