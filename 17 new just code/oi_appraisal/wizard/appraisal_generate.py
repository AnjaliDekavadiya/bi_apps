'''
Created on Nov 13, 2018

@author: Zuhair Hammadi
'''
from odoo import models, fields
from ast import literal_eval

class AppraisalGenerate(models.TransientModel):
    _name = 'appraisal.generate'
    _description = 'Appraisal Generate'
    
    phase_id = fields.Many2one('appraisal.phase')
    
    def generate(self):
        batch = self.env['appraisal.batch'].browse(self._context.get('active_id'))
        
        domain = literal_eval(batch.type_id.domain or '[]')
        model = batch.type_id.model_id.model or 'hr.employee'
        
        employee_ids = self.env[model].search(domain)
        
        if employee_ids._name =='hr.contract':
            employee_ids = employee_ids.employee_id
                                    
        for employee in employee_ids:
            self._generate(batch, employee, self.phase_id)            
        
        self.env.add_to_compute(batch.appraisal_ids._fields['parent_id'], batch.appraisal_ids)
        
        self._reset_parent_objective_id(batch)
                    
        return batch.action_view_appraisal()

    def _generate(self, batch, employee, phase_id):
        if self.env['appraisal'].search([('batch_id','=', batch.id), ('employee_id','=', employee.id), ('phase_id','=', phase_id.id)], limit = 1):
            return self.env['appraisal']
        
        template_id = employee.job_id.appraisal_template_ids.filtered(lambda a : a.phase_id == phase_id)
        if not template_id:
            return self.env['appraisal']
        appraisal = self.env['appraisal'].create({
            'batch_id' : batch.id,
            'employee_id' : employee.id,
            'template_id' : template_id.id,
            'phase_id' : phase_id.id
            })
        
        if template_id.copy_objectives and appraisal.previous_phase_id:
            for objective in appraisal.previous_phase_id.objective_ids:
                objective.copy({
                    'appraisal_id' : appraisal.id,
                    'original_objective_id' : objective.id
                    })
        
        return appraisal
    
    def _reset_parent_objective_id(self, batch):
        for appraisal in batch.appraisal_ids:
            for objective in appraisal.objective_ids:
                if objective.parent_objective_id and objective.parent_objective_id.appraisal_id.batch != batch:
                    objective.parent_objective_id = self.env['appraisal.objective'].search([('original_objective_id' ,'=', objective.parent_objective_id.id,)]).filtered(lambda o: o.appraisal_id.batch == batch)[:1]                                        
            
        