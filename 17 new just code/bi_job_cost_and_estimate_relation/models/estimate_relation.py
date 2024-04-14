# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import datetime
from odoo.exceptions import UserError, ValidationError



class JobEstimationWizard(models.TransientModel):
    _name = 'job.estimation.wizard'
    _description="Job estimation wizard"

    @api.model
    def default_get(self, fields):
        rec = super(JobEstimationWizard, self).default_get(fields)
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_id = context.get('active_id')
        if active_id:
            cost_sheet = self.env['job.cost.sheet'].browse(active_id)
            rec.update({'partner_id': cost_sheet.job_issue_customer_id.id})
        return rec
    
    partner_id = fields.Many2one('res.partner',string="Customer")
    pricelist_id = fields.Many2one('product.pricelist',string="Price List")
    
    def get_company_id(self):
        user_id = self.env.uid
        res_user_id = self.env['res.users'].browse(user_id)
        return res_user_id.id
    
    def create_job_estimation(self):
        record_id = self._context.get('active_id')
        your_class_records = self.env['job.cost.sheet'].browse(record_id)
        for rec in self:
            estimate_id = self.env['job.estimate'].create({
                'partner_id' : rec.partner_id.id,
                'payment_term_id' : rec.partner_id.property_payment_term_id.id or False,
                'pricelist_id' : rec.pricelist_id.id,
                'job_cost_sheet_id':your_class_records.id,
                'analytic_id':your_class_records.analytic_ids.id,
                'date':your_class_records.create_date,
                'company_id':self.get_company_id(),
                'currency_id':your_class_records.currency_id.id,
                'project_id':your_class_records.project_id.id,
            })
            for line in your_class_records.material_job_cost_line_ids:
                self.env['material.estimate'].create({
                    'material_id':estimate_id.id,
                    'type':'material',
                    'product_id':line.product_id.id,
                    'description':line.description,
                    'quantity':line.quantity,
                    'uom_id':line.uom_id.id,
                    'unit_price':line.unit_price,
                    'subtotal' : line.subtotal,
                    'currency_id':line.currency_id.id,})
            for line in your_class_records.labour_job_cost_line_ids:
                self.env['labour.estimate'].create({
                    'labour_id':estimate_id.id,
                    'type':'labour',
                    'product_id':line.product_id.id,
                    'uom_id':line.uom_id.id,
                    'description':line.description,
                    'quantity':line.quantity,
                    'hours':line.hours,
                    'unit_price':line.unit_price,
                    'subtotal' : line.subtotal,
                    'currency_id':line.currency_id.id,})
            if your_class_records.overhead_job_cost_line_ids:
                for line in your_class_records.overhead_job_cost_line_ids:
                    self.env['overhead.estimate'].create({
                        'overhead_id':estimate_id.id,
                        'type':'overhead',
                        'product_id':line.product_id.id,
                        'description':line.description,
                        'quantity':line.quantity,
                        'uom_id':line.uom_id.id,
                        'unit_price':line.unit_price,
                        'subtotal' : line.subtotal,
                        'currency_id':line.currency_id.id,})
            
            
class JobEstimate(models.Model):
    _inherit = 'job.estimate'
    
    pricelist_id = fields.Many2one('product.pricelist',string="Price List")
    job_cost_sheet_id = fields.Many2one('job.cost.sheet',string="Job Cost Sheet")
    
    def action_job_cost_estimation(self):
        self.ensure_one()
        return {
            'name': 'Job Cost Sheet',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'job.cost.sheet',
            'domain': [('id', '=', self.job_cost_sheet_id.id)],
        }
    
class Jobcost(models.Model):
    _inherit = 'job.cost.sheet'

    estimation_count_is = fields.Integer(' Material Purchase Requisition ', compute='_get_estimation_count_is')

    def unlink(self):
        for jcs in self:
            if jcs.estimation_count_is > 0:
                raise UserError(_('Sorry !!! You cannot delete a job cost sheet if job estimation is created'))
        return super(Jobcost, self).unlink()

    def _get_estimation_count_is(self):
        for estimation in self:
            estimation_ids = self.env['job.estimate'].search([('job_cost_sheet_id','=',estimation.id)])
            estimation.estimation_count_is = len(estimation_ids)
    
    def action_job_estimation(self):
        self.ensure_one()
        return {
            'name': 'Job Estimation',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'job.estimate',
            'domain': [('job_cost_sheet_id', '=', self.id)],
        }
    


