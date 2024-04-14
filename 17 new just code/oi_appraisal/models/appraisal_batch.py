'''
Created on Mar 26, 2023

@author: Zuhair Hammadi
'''
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AppraisalBatch(models.Model):    
    _name = 'appraisal.batch'
    _description = 'Appraisal Batch'
    _order = 'start_date desc'
    
    name = fields.Char(required = True)
    active = fields.Boolean(default = True)    
    start_date = fields.Date('Start Date', required = True)
    end_date = fields.Date('End Date', required = True)    
    year = fields.Char(compute ='_calc_year', store = True)
    
    appraisal_ids = fields.One2many('appraisal', 'batch_id')
    appraisal_count = fields.Integer(compute = '_calc_appraisal_count')
    appraisal_draft_count = fields.Integer(compute = '_calc_appraisal_count')
    
    evaluation_ids = fields.One2many('appraisal.evaluation', 'batch_id')
    evaluation_count = fields.Integer(compute = '_calc_evaluation_count')
    
    type_id = fields.Many2one('appraisal.batch.type', required = True)    
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
            
    _sql_constraints= [
            ('name_unqiue', 'unique(name)', 'Name must be unique!')
        ]        
    
    @api.onchange('name')
    def _onchange_name(self):
        if self.name and self.name.isdigit() and len(self.name)==4 and self.name[0]=='2':
            self.start_date = '%s-01-01' % self.name
            self.end_date = '%s-12-31' % self.name
    
    @api.constrains('start_date', 'end_date')
    def _check_date(self):
        for record in self:
            if record.start_date and record.end_date and record.start_date > record.end_date:
                raise ValidationError(_('Start Date > End Date'))
    
    @api.depends('end_date')
    def _calc_year(self):
        for record in self:
            record.year = record.end_date and record.end_date.year
    
    @api.depends('appraisal_ids')
    def _calc_appraisal_count(self):
        for record in self:
            domain = [('batch_id', '=', record.id)]
            record.appraisal_count = self.env['appraisal'].search_count(domain)
            domain.append(('state','=', 'draft'))
            record.appraisal_draft_count = self.env['appraisal'].search_count(domain)
            
    @api.depends('evaluation_ids')
    def _calc_evaluation_count(self):
        for record in self:
            record.evaluation_count = len(record.evaluation_ids)            
                        
    
    def action_view_appraisal(self):
        action, = self.env.ref('oi_appraisal.act_appraisal').read()
        action['domain'] = [('batch_id', 'in', self.ids)]
        return action
    
    
    def action_submit_appraisal(self):
        count = 0
        for appraisal in self.appraisal_ids:
            if appraisal.state=='draft':
                appraisal.action_approve()
                count +=1
        if hasattr(self.env.user,'notify_info'):
            self.env.user.notify_info(_('%s Appraisal(s) Submitted') % count)
            
    def action_view_evaluation(self):
        return {
            'type' : 'ir.actions.act_window',
            'name' : _('Evaluations'),
            'res_model' : 'appraisal.evaluation', 
            'view_mode' : 'tree,form',
            'domain' : [('batch_id','=', self.id)],
            'context' : {
                'default_batch_id' : self.id
                }
            }                                            
        
    
