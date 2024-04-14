'''
Created on Apr 30, 2023

@author: Zuhair Hammadi
'''
from odoo import models, fields, api

class AppraisalObjective(models.Model):    
    _name = 'appraisal.objective'    
    _description='Appraisal Objective'
    _order = 'sequence,id'

    appraisal_id = fields.Many2one('appraisal', required = True, ondelete='cascade', index = True)
    name = fields.Char(required = True)
    sequence = fields.Integer()
    target_date = fields.Date()
    
    display_type = fields.Selection([
        ('line_section', "Section"),
        ], default=False)

    parent_objective_id = fields.Many2one('appraisal.objective', string='Manager Objective')
    description = fields.Text()
    weight = fields.Float(compute = '_calc_weight', store = True, recursive=True)
    
    section_id = fields.Many2one('appraisal.objective', compute = '_calc_section_id', store = True, recursive = True, copy = False)
    child_ids = fields.One2many('appraisal.objective','section_id')
    
    original_objective_id = fields.Many2one('appraisal.objective' , copy = False)
    
    is_ad_hoc = fields.Boolean()
    
    @api.depends('appraisal_id.objective_ids.sequence')
    def _calc_section_id(self):
        for record in self:
            section_id = False
            if not record.display_type:
                for objective in record.appraisal_id.objective_ids.sorted():
                    if objective._origin == record._origin:
                        break
                    if objective.is_ad_hoc != record.is_ad_hoc:
                        continue
                    if objective.display_type:
                        section_id = objective
            record.section_id = section_id
                
    @api.depends('child_ids.weight')
    def _calc_weight(self):
        for record in self:
            if record.display_type:
                record.weight = sum(record.mapped('child_ids.weight'))