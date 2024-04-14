# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import UserError


class CarRepairSupport(models.Model):
    _inherit="car.repair.support"
    
    labour_jobcost_line_ids = fields.One2many(
        'car.jobcost.line',
        'car_support_id',
        string="Labour Cost Line",
        copy=False,
        domain=[('job_type','=','labour')],
    )
    overhead_jobcost_line_ids = fields.One2many(
        'car.jobcost.line',
        'car_support_id',
        string="Overhead Cost Line",
        copy=False,
        domain=[('job_type','=','overhead')],
    )
    jobcost_sheet_id = fields.Many2one(
        'job.costing',
        string="Jobs Sheet",
        readonly=True,
        copy=False,
    )
    
    def _prepare_line_product_change(self, jobcost_line_vals):
        jobcost_line = self.env['job.cost.line'].new(jobcost_line_vals)
        jobcost_line._onchange_product_id()
        jobcost_line_values = jobcost_line._convert_to_write({name: jobcost_line[name] for name in jobcost_line._cache})
        return jobcost_line_values
    
    
    def _prepare_jobcost_vals(self, job_type):
        if  job_type == 'material':
            material_jobcost_vals = {}
            cost_line_lst = []
            for material in self.cosume_part_ids:
                material_jobcost_vals.update({
                    'date': fields.Date.today(),
                    'job_type': material.job_type,
                    'job_type_id': material.job_type_id.id,
                    'product_id': material.product_id.id
                })
                jobcost_line_values = self._prepare_line_product_change(material_jobcost_vals)
                jobcost_line_values['product_qty'] = material.qty
                cost_line_lst.append((0,0,jobcost_line_values))
            return cost_line_lst

        if  job_type == 'labour':
            labour_jobcost_vals = {}
            labour_cost_line_lst = []
            for labour in self.labour_jobcost_line_ids:
                labour_jobcost_vals.update({
                    'date': fields.Date.today(),
                    'job_type': labour.job_type,
                    'job_type_id': labour.job_type_id.id,
                    'product_id': labour.product_id.id,
                    'hours': labour.hours,
                })
                jobcost_line_values = self._prepare_line_product_change(labour_jobcost_vals)
                labour_cost_line_lst.append((0,0,jobcost_line_values))
            return labour_cost_line_lst
        
        if  job_type == 'overhead':
            overhead_jobcost_vals = {}
            overhead_cost_line_lst = []
            for overhead in self.overhead_jobcost_line_ids:
                overhead_jobcost_vals.update({
                    'date': fields.Date.today(),
                    'job_type': overhead.job_type,
                    'job_type_id': overhead.job_type_id.id,
                    'product_id': overhead.product_id.id,
                })
                jobcost_line_values = self._prepare_line_product_change(overhead_jobcost_vals)
                jobcost_line_values['product_qty'] = overhead.product_qty
                overhead_cost_line_lst.append((0,0,jobcost_line_values))
            return overhead_cost_line_lst
        return []
    
    def _prepare_jobcostsheet_vals(self):
        jobcost_sheet_vals = {
            'name': (self.subject or '') + ' ' + self.name,
            'partner_id': self.partner_id.id,
            'project_id': self.project_id.id,
            'analytic_id': self.analytic_account_id.id,
        }
        return jobcost_sheet_vals
    
    #@api.multi
    def create_jobcost(self):
        for rec in self:
            if not rec.partner_id:
                raise UserError("Please Set Customer on Car repair")
            material_jobcost_vals = self._prepare_jobcost_vals(job_type='material')
            labour_jobcost_vals = self._prepare_jobcost_vals(job_type='labour')
            overhead_jobcost_vals = self._prepare_jobcost_vals(job_type='overhead')
            jobcost_sheet_vals = self._prepare_jobcostsheet_vals()
            jobcost_sheet_vals.update({
                'job_cost_line_ids': material_jobcost_vals,
                'job_labour_line_ids': labour_jobcost_vals,
                'job_overhead_line_ids': overhead_jobcost_vals,
                'car_support_id': rec.id
            })
            jobcost_sheet_id = self.env['job.costing'].create(jobcost_sheet_vals)
            rec.jobcost_sheet_id = jobcost_sheet_id.id
    
    #@api.multi
    def show_jobcost_sheet(self):
        self.ensure_one()
        # action = self.env.ref("odoo_job_costing_management.action_job_costing").sudo().read()[0]
        action = self.env['ir.actions.actions']._for_xml_id('odoo_job_costing_management.action_job_costing')
        # action['domain'] = [('id', 'in', self.jobcost_sheet_id.ids)]
        action['domain'] = [('car_support_id', '=', self.id)]
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
