# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ProjectQualityControlPoint(models.Model):
   
    _name = 'project.quality.control.point'
    _description = "Project Quality Control Point"
    _rec_name = 'control_point_no'
    

    title = fields.Char(
        string= 'Title',
        required= True
    )
    control_point_no = fields.Char(
        string='Reference',
        readonly=True,
        copy=False
    )
    team_id = fields.Many2one(
        'project.quality.team',
        string='Team',
        required=True
    )
    responsible_user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
        required=True
    )
    type_id = fields.Many2one(
        'project.quality.type',
        string='Type',
        required=True
    )
    instruction = fields.Html(
        string='Instruction',
        required=True
    )
    notes = fields.Text(
        string='Internal Notes',
        copy=True,
    )

    @api.model
    def create(self, vals): 
        vals['control_point_no'] = self.env['ir.sequence'].next_by_code('project.quality.control.point')
        return super(ProjectQualityControlPoint,self).create(vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:       
