# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import UserError

class ClothRequestDetails(models.Model):
    _inherit="cloth.request.details"
    
    project_id = fields.Many2one(
        'project.project',
        string='Project',
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string="Analytic Account",
    )
    material_jobcost_line_ids = fields.One2many(
        'cloth.jobcost.line',
        'cloth_request_id',
        string="Material Cost Line",
        copy=True,
        domain=[('job_type','=','material')],
    )
    labour_jobcost_line_ids = fields.One2many(
        'cloth.jobcost.line',
        'cloth_request_id',
        string="Labour Cost Line",
        copy=True,
        domain=[('job_type','=','labour')],
    )
    overhead_jobcost_line_ids = fields.One2many(
        'cloth.jobcost.line',
        'cloth_request_id',
        string="Overhead Cost Line",
        copy=True,
        domain=[('job_type','=','overhead')],
    )
    
    def show_jobcost_sheet(self):
        self.ensure_one()
        # action = self.env.ref("odoo_job_costing_management.action_job_costing").sudo().read()[0]
        action = self.env['ir.actions.actions']._for_xml_id('odoo_job_costing_management.action_job_costing')
        action['domain'] = [('cloth_request_id','=', self.id)]
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
