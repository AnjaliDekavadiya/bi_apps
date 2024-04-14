'''
Created on Mar 15, 2023

@author: Zuhair Hammadi
'''
from odoo import models, fields, api

class AppraisalTemplate(models.Model):    
    _name = 'appraisal.template'
    _inherit = ['appraisal.name.mixin']
    _description = 'Appraisal Template'
    _order = 'sequence,id'
    
    @api.model
    def _get_appriasal_state(self):
        return self.env['appraisal']._get_state()
    
    sequence = fields.Integer()
    phase_id = fields.Many2one('appraisal.phase')
    line_ids = fields.One2many('appraisal.template.line', 'template_id', copy = True)
    
    job_ids = fields.Many2many('hr.job', string='Job Positions')
    
    rating_type_id = fields.Many2one('appraisal.rate', domain = [('type','=', 'result')])
    
    show_objectives = fields.Boolean(default = True)
    show_manager_objectives = fields.Boolean(default = True)
    show_ad_hoc = fields.Boolean()
    copy_objectives = fields.Boolean('Copy objectives from previous phase', default = True)
    
    objectives_write_states = fields.Json('Enable Objectives Updates On Status')
    
    evaluation_status = fields.Selection(_get_appriasal_state, string="Create Evaluation On Status")
    result_status = fields.Selection(_get_appriasal_state, string="Calculate Result On Status")
    