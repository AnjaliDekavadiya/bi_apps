# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime, date
from odoo import models, fields, api, SUPERUSER_ID,  _
from odoo.exceptions import UserError
from odoo.osv import expression

class JobSheetLink(models.TransientModel):
    _name = 'job.sheet.link'
    _description = "job sheet link"

    name = fields.Char('Job Cost Sheet name')
    job_link = fields.Selection([
        ('create', 'Create Job Cost Sheet'), 
        ('update', 'Update Job Cost Sheet')], string='Options', required=True)
    jobcost_sheet_id = fields.Many2one('job.cost.sheet','Job Cost Sheet',)
    project_id = fields.Many2one('project.project',string='Project',required=True)

    @api.model
    def default_get(self, fields):
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_id')
        jobs = self.env[active_model].browse(active_ids)
        rec = {}
        if not len(jobs.material_planning_ids) >= 1:
            raise UserError(_('Select Material planning lines!!'))

        rec.update({
            'job_link' : 'create',
            'project_id' : jobs.project_id.id,
            'jobcost_sheet_id' : jobs.jobcost_order_id.id or False,
            })
        return rec

    def job_sheet_link(self):
        for link in self:
            user_id = self.env.uid
            joborder_obj = self.env['job.order']
            jobcostsheet_obj = self.env['job.cost.sheet']
            material_planning_obj = self.env['material.planning']

            res_user_id = self.env['res.users'].browse(user_id)
            joborder = joborder_obj.browse(self.env.context.get('active_id'))
            planning_ids = material_planning_obj.search([('material_id','=',joborder.id)])

            if link.job_link == 'create':
                vals = {
                'name' : link.name,
                'create_date' : datetime.now(),
                'close_date' : joborder.end_date,
                'project_id' : link.project_id.id,
                'job_order_id' : joborder.id,
                'create_by_id' : joborder.user_id.id,
                'company_id' : res_user_id.company_id.id,
                }
                job_cost_id = jobcostsheet_obj.create(vals)
                joborder.write({'jobcost_order_id' : job_cost_id.id})
                for plan in planning_ids:
                    plan.write({'jobcost_material_id':job_cost_id.id})
                jobcostsheet_objo = self.env['job.cost.sheet'].search([('job_order_id','=',joborder.id)])
                material_list = []
                labour_list = []
                overhead_list = []
                for line in joborder.material_planning_ids:
                    if line.job_type_id.job_type == 'material':
                        material_list.append((0,0,{
                        'date' : datetime.now(),
                        'job_type_id' : line.job_type_id.id,
                        'product_id' : line.product_id.id,
                        'unit_price' : line.product_id.lst_price,
                        'description' : line.description,
                        'quantity' : line.quantity,
                        'uom_id' : line.uom_id.id,
                        'currency_id' : res_user_id.company_id.currency_id.id,
                        }))
                        
                    elif line.job_type_id.job_type == 'labour':
                        jobcostsheet_objo = self.env['job.cost.sheet'].search([('job_order_id','=',joborder.id)])
                        labour_list.append((0,0,{
                        'date' : datetime.now(),
                        'job_type_id' : line.job_type_id.id,
                        'product_id' : line.product_id.id,
                        'unit_price' : line.product_id.lst_price,
                        'description' : line.description,
                        'hours' : line.quantity,
                        'uom_id' : line.uom_id.id,
                        'currency_id' : res_user_id.company_id.currency_id.id,
                        }))
                    else:
                        jobcostsheet_objo = self.env['job.cost.sheet'].search([('job_order_id','=',joborder.id)])
                        overhead_list.append((0,0,{
                        'date' : datetime.now(),
                        'job_type_id' : line.job_type_id.id,
                        'product_id' : line.product_id.id,
                        'unit_price' : line.product_id.lst_price,
                        'description' : line.description,
                        'quantity' : line.quantity,
                        'uom_id' : line.uom_id.id,
                        'currency_id' : res_user_id.company_id.currency_id.id,
                        }))
                vals = {
                        'material_job_cost_line_ids' : material_list,
                        }
                for rec in jobcostsheet_objo:
                    job_cost_id = rec.write(vals)
                vals = {
                        'overhead_job_cost_line_ids' : overhead_list,
                        }
                for rec in jobcostsheet_objo:
                    job_cost_id = rec.write(vals)
                vals = {
                        'labour_job_cost_line_ids' : labour_list,
                        }
                for rec in jobcostsheet_objo:
                    job_cost_id = rec.write(vals)
                return {'type': 'ir.actions.act_window_close'} 

            if link.job_link == 'update':
                if (link.jobcost_sheet_id == joborder.jobcost_order_id):
                    material_list = []
                    labour_list = []
                    overhead_list = []
                    jobcost = jobcostsheet_obj.browse(link.jobcost_sheet_id.id)
                    jobcost.material_job_cost_line_ids.unlink()
                    jobcost.overhead_job_cost_line_ids.unlink()
                    jobcost.labour_job_cost_line_ids.unlink()
                    for line in joborder.material_planning_ids:
                        if line.job_type_id.job_type == 'material':
                            material_list.append((0,0,{
                            'date' : datetime.now(),
                            'job_type_id' : line.job_type_id.id,
                            'product_id' : line.product_id.id,
                            'unit_price' : line.product_id.lst_price,
                            'description' : line.description,
                            'quantity' : line.quantity,
                            'uom_id' : line.uom_id.id,
                            'currency_id' : res_user_id.company_id.currency_id.id,
                            }))             
                                
                        elif line.job_type_id.job_type == 'labour':
                            labour_list.append((0,0,{
                            'date' : datetime.now(),
                            'job_type_id' : line.job_type_id.id,
                            'product_id' : line.product_id.id,
                            'unit_price' : line.product_id.lst_price,
                            'description' : line.description,
                            'hours' : line.quantity,
                            'uom_id' : line.uom_id.id,
                            'currency_id' : res_user_id.company_id.currency_id.id,
                            }))             
                            
                        else:
                            overhead_list.append((0,0,{
                            'date' : datetime.now(),
                            'job_type_id' : line.job_type_id.id,
                            'product_id' : line.product_id.id,
                            'unit_price' : line.product_id.lst_price,
                            'description' : line.description,
                            'quantity' : line.quantity,
                            'uom_id' : line.uom_id.id,
                            'currency_id' : res_user_id.company_id.currency_id.id,
                            }))  

                    jobcost.write({'material_job_cost_line_ids':material_list})
                    jobcost.write({'overhead_job_cost_line_ids':overhead_list})
                    jobcost.write({'labour_job_cost_line_ids':labour_list})
                    
                    for plan in planning_ids:
                        plan.write({'jobcost_material_id':jobcost.id})
                    return {'type': 'ir.actions.act_window_close'}
                else:
                    raise UserError(_("Update could not process, You're Trying to Update Wrong Cost Sheet.")) 
        return {'type': 'ir.actions.act_window_close'} 

class MaterialPlanningInherit(models.Model):
    _inherit = "material.planning"

    jobcost_material_id = fields.Many2one('job.cost.sheet','Job Cost Sheet',readonly=True)


class JobOrderInherit(models.Model):
    _inherit = "job.order"

    jobcost_order_id = fields.Many2one('job.cost.sheet','Job Cost Sheet',readonly=True)


class JobOrderSheetInherit(models.Model):
    _inherit = "job.cost.sheet"
    _rec_name = 'sequence'

    def name_get(self):
        if self._context:
            res = []
            for order in self:
                name = order.sequence
                res.append((order.id, name))
            return res
        return super(JobOrderSheetInherit, self).name_get()


    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, order=None):
        if operator in ('ilike', 'like', '=', '=like', '=ilike'):
            domain = expression.AND([
                args or [],
                [('sequence', operator, name)]
            ])
            return self._search(domain, limit=limit, order=order)
        return super(JobOrderSheetInherit, self)._name_search(name, args, operator, limit, order)

