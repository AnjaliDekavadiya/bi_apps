# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _


class JobCostLine(models.Model):
    _inherit = "job.cost.line"

    material_project_id = fields.Many2one('project.project',related="material_job_cost_sheet_id.project_id",string='Project',store=True,readonly=True)
    labour_project_id = fields.Many2one('project.project',related="labour_job_cost_sheet_id.project_id",string=' Project',store=True,readonly=True)
    overhead_project_id = fields.Many2one('project.project',related="overhead_job_cost_sheet_id.project_id",string=' Project ',store=True,readonly=True)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order'    

    project_id = fields.Many2one('project.project')

class InvoiceLine(models.Model):
    _inherit = 'account.move'  

    project_id = fields.Many2one('project.project')