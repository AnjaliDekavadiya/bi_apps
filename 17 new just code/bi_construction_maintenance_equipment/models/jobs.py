from odoo import fields, models, api
from datetime import datetime, timedelta, date


class MaintenanceReqInherit(models.Model):
    _inherit = 'maintenance.request'

    project_id = fields.Many2one('project.project', "Project")


class InheritJobOrder(models.Model):
    _inherit = "job.order"

    maintenance_req_count = fields.Integer(' Maintenance Request', compute='_get_maintenance_req_count')

    def _get_maintenance_req_count(self):
        for req in self:
            req_ids = self.env['maintenance.request'].search([('job_order_id', '=', req.id)])
            req.maintenance_req_count = len(req_ids)

    def action_view_maintenance_request(self):
        self.ensure_one()
        return {
            'name': 'Maintenance Requests',
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban,form',
            'res_model': 'maintenance.request',
            'domain': [('job_order_id', '=', self.id)],
        }


class InheritProject(models.Model):
    _inherit = 'project.project'

    maintenance_req_count = fields.Integer('Maintenance Request', compute='_get_maintenance_req_count')

    def _get_maintenance_req_count(self):
        for req in self:
            req_ids = self.env['maintenance.request'].search([('project_id', '=', req.id)])
            req.maintenance_req_count = len(req_ids)

    def action_view_maintenance_request(self):
        self.ensure_one()
        return {
            'name': 'Projects',
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban,form',
            'res_model': 'maintenance.request',
            'domain': [('project_id', '=', self.id)],
        }
