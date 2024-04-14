# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProjectQualityControlAlert(models.Model):
    
    _name = 'project.quality.alert'
    _description = "Project Quality Control Alert"
    _rec_name = 'alert_no'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    title = fields.Char(
        string= 'Title',
        required= True
    )
    
    alert_no = fields.Char(
        string='Reference',
        readonly=True,
        copy=False
    )
    
    state = fields.Selection(
        [('new','New'),
         ('confirmed','Confirmed'),
         ('action proposed','Action Proposed'),
         ('solved','Solved'),
        ],
        string='Stage',
        default='new',
        tracking=True,
        copy=False, 
    )
    
    project_quality_check_id = fields.Many2one(
        'project.quality.check',
        string="Check",
    )
    
    task_id = fields.Many2one(
        'project.task',
        string="Task",
    )
    
    project_id = fields.Many2one(
        'project.project',
        string="Project",
    )
    
    team_id = fields.Many2one(
        'project.quality.team',
        string='Team',
    )
    
    responsible_user_id = fields.Many2one(
        'res.users',
        string='Responsible',
    )
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Very High'),], 
        default='0',
        string="Priority"
    )
    
    description = fields.Html(
        string='Description',
    )
    
    alert_action_corrective = fields.Html(
        string='Corrective Actions',
    )
    
    alert_action_preventive = fields.Html(
        string='Preventive Actions',
    )
    
    quality_tag_ids = fields.Many2many(
        'project.quality.tag',
        string='Tags',
    )
    
    quality_reason_id = fields.Many2one(
        'project.quality.reason',
        string='Reason',
        copy=False,
    )
    
    @api.model
    def create(self, vals): 
        vals['alert_no'] = self.env['ir.sequence'].next_by_code('project.quality.alert')
        return super(ProjectQualityControlAlert,self).create(vals)
        
    #@api.multi
    def action_button_quality_check(self):
        self.ensure_one()
        action = self.env.ref("project_task_quality_management.action_project_quality_check").read([])[0]
        action['domain'] = [('id','=',self.project_quality_check_id.id)]
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:       
