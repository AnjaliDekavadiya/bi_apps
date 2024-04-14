# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)
from odoo.tools import html2plaintext

class AccountAnalyticLineSubc(models.Model):
    _inherit = "account.analytic.line"
    
    sub_account_analytic_line_id = fields.Many2one('job.subcontract','Job Subcontract')

class JobCostSheet(models.Model):
    _inherit = "job.cost.sheet"
    
    sub_con_id = fields.Many2one('job.subcontract','Job Subcontract')
        
class JobSubContract(models.Model):
    _name = 'job.subcontract'
    _description = 'Job Subcontract'

    
    name = fields.Char(string="Name",required=True)
    active = fields.Boolean(default=True)
    priority = fields.Selection([('0','Low'), ('1','Normal'), ('2','High')], 'Priority')
    description = fields.Text('Description')
    subcontractor_job_order = fields.Boolean('Subcontractor Job Order')
    
    project_id = fields.Many2one('project.project',string='Project')
    job_order_id = fields.Many2one('job.order','Job Order')
    job_issue_customer_id = fields.Many2one('res.partner','Job Issue Customer')
    assigned_to = fields.Many2one('res.users','Assigned to')
    subcontractor_id = fields.Many2one('res.partner', 'Sub Contractor')
    create_date = fields.Datetime(string="Starting Date",default=datetime.now())
    close_date = fields.Datetime(string="Ending Date")
    deadline = fields.Datetime(string='Deadline')
    
    purchase_line_ids = fields.One2many('sub.purchase.line', 'subcontract_id', 'Purchase Order Lines')
    timesheet_ids = fields.One2many('account.analytic.line','sub_account_analytic_line_id',string="Timesheet")
    material_planning_ids = fields.One2many('material.planning','subcontract_id',string="Material Planning")
    consumed_material_ids = fields.One2many('material.planning','consumed_material_sub_id',string=" Consumed Material")
    material_requisitions_ids = fields.One2many('material.purchase.requisition','m_requisition_subc_id',string="Material Requisitions")
    subtask_ids = fields.One2many('project.task','task_subcontract_id',string=" Subtask ")
    
    subtask_count = fields.Integer('Subtask', compute='_get_subtask_count')
    stock_move_count = fields.Integer('Stock Move')
    job_cost_sheet_count = fields.Integer('Job Cost Sheet', compute='_get_job_cost_sheet_count')
    
    def _get_job_cost_sheet_count(self):
        for job_sheet in self:
            job_sheet_ids = self.env['job.cost.sheet'].search([('sub_con_id','=',job_sheet.id)])
            job_sheet.job_cost_sheet_count = len(job_sheet_ids)
        
    def job_cost_sheet_button(self):
        self.ensure_one()
        return {
            'name': 'Job Cost Sheet',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'job.cost.sheet',
            'domain': [('sub_con_id', '=', self.id)],
        }
        

    def subtask_button(self):
        self.ensure_one()
        return {
            'name': 'Sub Task',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'project.task',
            'domain': [('task_subcontract_id', '=', self.id)],
        } 
    
    def purchase_button(self):
        self.ensure_one()
        return {
            'name': 'Purchase Order',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'domain': [('subcontract_id', '=', self.id)],
        }        

    
    def _get_stock_move_count_subcontract(self):
        for job_order in self:
            stock_move_ids = self.env['stock.move'].search([('stock_move_id','=',job_order.id)])
            job_order.stock_move_count = len(stock_move_ids)
    
    def _get_subtask_count(self):
        for subc in self:
            subtask_ids = self.env['project.task'].search([('task_subcontract_id','=',subc.id)])
            subc.subtask_count = len(subtask_ids)

   
class SubContractPurchaseLine(models.Model):
    _name = 'sub.purchase.line'
    _description = 'Sub Purchase Line'
    
    product_id = fields.Many2one('product.product', 'Product')
    name = fields.Char('Description')
    analytic_ids = fields.Many2one('account.analytic.account',string="Analytic Account")
    qty = fields.Float('Quantity',default=1.0)
    uom_id = fields.Many2one('uom.uom','Unit Of Measure')
    subcontract_id = fields.Many2one('job.subcontract','Sub Contract')

    @api.onchange('product_id')
    def onchange_product_id(self):
        product = self.product_id
        self.name = product.partner_ref
        self.uom_id = product.uom_id.id
        return {'domain': {'uom_id': [('category_id', '=', product.uom_id.category_id.id)]}}
    
class MaterialPlanningSubc(models.Model):
    _inherit = "material.planning"
    
    subcontract_id = fields.Many2one('job.subcontract','Job Subcontract')
    consumed_material_sub_id = fields.Many2one('job.subcontract',' Job Consumed Material')

'''class MaterialPlanningSubc(models.Model):
    _inherit = "consumed.material"
    
    subcontract_id = fields.Many2one('job.subcontract','Job Subcontract')'''

class MaterialRequisitions(models.Model):
    _inherit = 'material.purchase.requisition'
    
    m_requisition_subc_id = fields.Many2one('job.subcontract','Job Subcontract') 

class StockPicking(models.Model):
    _inherit = 'project.task'
    
    task_subcontract_id = fields.Many2one('job.subcontract','Job Subcontract') 

class SubcontractPurchase(models.Model):
    
    _inherit = 'purchase.order'
    
    subcontract_id = fields.Many2one('job.subcontract','Job Subcontract')  


class JobOrder(models.Model):
    _inherit = 'job.order'

    contract_count = fields.Integer(compute='_compute_contract_count',string='Contract Count',default=0)

    def _compute_contract_count(self):
        for job in self:
            contract = self.env['job.subcontract'].search([('job_order_id', '=', job.id)])
            job.contract_count = len(contract)


    def contract_button(self):
        self.ensure_one()
        return {
            'name': 'Job Subcontract',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'job.subcontract',
            'domain': [('job_order_id', '=', self.id)],
        }