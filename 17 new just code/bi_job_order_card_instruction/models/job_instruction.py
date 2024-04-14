# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
##############################################################################

from odoo import api, fields, models, _

class checklist(models.Model):
    _name = 'quality.checklist'
    _description = "quality checklist"
    
    name = fields.Char('Name')
    code = fields.Char('Code')


class ir_attachment(models.Model):
    _inherit = 'ir.attachment'

    job_instruction_id = fields.Many2one('job.instruction') 
    job_instruction_details_id = fields.Many2one('job.instruction.details')  

class job_instruction_details(models.Model):
    _name = 'job.instruction.details'
    _description = "job instruction"
     
    name =fields.Char('Name')      
    job_instruction_id = fields.Many2one('job.instruction','Job Instruction')
    quality_checklist_ids = fields.Many2many('quality.checklist',string='Quality Checklist')
    date  = fields.Date('Date')
    user_id = fields.Many2one('res.users','Responsible User')
    supervisior_id = fields.Many2one('res.users','Supervisor')
    job_id = fields.Many2one('job.order','Job')
    description = fields.Text('Description')
    attachment_ids = fields.One2many('ir.attachment','job_instruction_details_id')
    state = fields.Selection([('draft','Draft'), ('start', 'Start'), ('pause','Pause'), ('finished','Finished')] , default='draft')

    def to_start(self):
        for job_order in self:
            job_order.state = 'start'

    def to_pause(self):
        for job_order in self:
            job_order.state = 'pause'

    def to_restart(self):
        for job_order in self:
            job_order.state = 'start'

    def to_finish(self):
        for job_order in self:
            job_order.state = 'finished'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('ins_seq') or 'INSTRUCTION'
        result = super(job_instruction_details, self).create(vals_list)
        return result  

class job_instruction(models.Model):
    _name = 'job.instruction'
    _description = "job instruction"
    
    name = fields.Char('Name')
    code = fields.Char('Code')
    attachment_ids = fields.One2many('ir.attachment','job_instruction_id')

class job_order(models.Model):
    _inherit = 'job.order'

    def _get_number_of_instruction(self):
        for job_order in self:
            job_instruction_ids = self.env['job.instruction.details'].search([('job_id', '=', self.id)])            
            job_order.count_of_instruction = len(job_instruction_ids)
         

    def button_view_instruction(self):
        instruction_list  = []
        instruction_ids = self.env['job.instruction.details'].search([('job_id', '=', self.id)])
        for instruction_id in instruction_ids:
            instruction_list.append(instruction_id.id)
        context = dict(self._context or {})
        return {
            'name': _('Instruction '),
            'view_mode': 'tree,form',
            'res_model': 'job.instruction.details',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in',instruction_list )],
            'context': context,
        }
    instruction_ids = fields.One2many('job.instruction.details','job_id',string='Job Instruction')
    count_of_instruction =  fields.Integer('Instruction',compute='_get_number_of_instruction')      

