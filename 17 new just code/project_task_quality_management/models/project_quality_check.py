# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProjectQualityCheck(models.Model):
    _name = 'project.quality.check'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Project Quality Check"
    _rec_name = 'alert_check_no'


    task_id = fields.Many2one(
        'project.task',
        string="Task",
        required=True
    )
    project_id = fields.Many2one(
        'project.project',
        string="Project",
        required=True
    )
    team_id = fields.Many2one(
        'project.quality.team',
        string='Team',
        required=True
    )
    notes = fields.Text(
        string='Notes',
        copy=True,
    )
    state = fields.Selection(
        [('to_do','To Do'),
         ('pass','Passed'),
         ('fail','Failed'),
        ],
        string='Status',
        default='to_do',
        tracking=True,
        copy=False, 
    )
    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        readonly=True, 
        default=lambda self: self.env.user.company_id
    )
    description = fields.Html(
        string='Description',
    )
    control_point_id = fields.Many2one(
        'project.quality.control.point',
        string='Control Point',
        required=True
    )
    project_quality_alert = fields.One2many(
        'project.quality.alert',
        'project_quality_check_id',
        string='Project Quality Alert',
    )
    
    check_user_id = fields.Many2one(
        'res.users',
        string='Checked By',
    )
    
    alert_check_no = fields.Char(
        string='Alert Check No',
        readonly=True,
        copy=False
    )
    
    check_date = fields.Date(
        string='Checked Date',
    )


    #@api.multi
    def action_to_do(self):
        return self.write({'state': 'to_do'})

    #@api.multi
    def action_pass(self):
        return self.write({'state': 'pass'})

    #@api.multi
    def action_fail(self):
        return self.write({'state': 'fail'})

    @api.onchange('project_id')
    def onchange_project_id(self):
        if self.project_id:
            if self.project_id != self.task_id.project_id:
                self.task_id = False
            return {'domain': {
                'task_id': [('project_id', '=', self.project_id.id)]
            }}


    #@api.multi
    def action_button_quality_alert(self):
        self.ensure_one()
        action = self.env.ref("project_task_quality_management.action_project_quality_alert").read([])[0]
        action['domain'] = [('project_quality_check_id','=',self.id)]
        return action
        
    #@api.multi
    def action_button_quality_point(self):
        self.ensure_one()
        action = self.env.ref("project_task_quality_management.action_project_quality_control_point").read([])[0]
        action['domain'] = [('id','=',self.control_point_id.id)]
        return action

    @api.model
    def create(self, vals): 
        vals['alert_check_no'] = self.env['ir.sequence'].next_by_code('project.quality.check')
        return super(ProjectQualityCheck,self).create(vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:       
