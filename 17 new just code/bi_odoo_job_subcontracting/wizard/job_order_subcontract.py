# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Project(models.TransientModel):
    _name = 'subcontract.job.order'
    _description = 'Subcontract Job Order'

    user_id = fields.Many2one('res.users','Responsible User/Sub Contractor User', required=True)
    job_id = fields.Many2one('job.order','Job',readonly=True,required=True)
    subcontractor_id = fields.Many2one('res.partner', 'Sub Contractor',required=True)
    job_desc = fields.Text('Job Description')
    
    @api.model 
    def default_get(self, flds): 
        result = super(Project, self).default_get(flds)
        job_id = self.env['job.order'].browse(self._context.get('active_id'))
        result['user_id'] = job_id.user_id.id
        result['job_id'] = job_id.id
        return result


    def create_subcontract_job_order(self):
        timesheet_list = []
        planning_list = []
        consumed_list = [] 
        requisition_list = []

        subcontract_obj = self.env['job.subcontract']
        current_jo = self.env['job.order'].browse(self._context.get('active_id'))
    
        for timesheet in current_jo.timesheet_ids:
            timesheet_list.append((0,0,{
                'date': timesheet.date,
                'employee_id': timesheet.employee_id.id,
                'name' : timesheet.name,
                'task_id' : timesheet.task_id.id,
                'unit_amount' : timesheet.unit_amount,
                'account_id' : timesheet.account_id.id,
                }))

        for material in current_jo.material_planning_ids:
            planning_list.append((0,0,{
                'job_type_id': material.job_type_id.id,
                'product_id': material.product_id.id,
                'description' : material.description ,
                'quantity' : material.quantity,
                'uom_id' : material.uom_id.id,
                }))    

        for consumed in current_jo.consumed_material_ids:
            consumed_list.append((0,0,{
                'product_id': consumed.product_id.id,
                'description' : consumed.description ,
                'quantity' : consumed.quantity,
                'uom_id' : consumed.uom_id.id,
                }))     

        for requisition in current_jo.material_requisitions_ids:
             requisition_list.append((0,0,{
                'sequence': requisition.sequence,
                'employee_id': requisition.employee_id.id,
                'department_id' : requisition.department_id.id ,
                'requisition_responsible_id' : requisition.requisition_responsible_id.id,
                'requisition_date' : requisition.requisition_date,
                'state' : requisition.state,
                'company_id' : requisition.company_id.id,
                }))
           
        subcontract_obj.create({
            'assigned_to': self.user_id.id,
            'project_id': self.job_id.project_id.id,
            'job_order_id' : self.job_id.id,
            'name': self.job_id.name,
            'subcontractor_id': self.subcontractor_id.id,
            'subcontractor_job_order': True,
            'description': self.job_desc,
            'timesheet_ids': timesheet_list,
            'material_planning_ids': planning_list,
            'consumed_material_ids': consumed_list,
            'material_requisitions_ids': requisition_list,

        })
       