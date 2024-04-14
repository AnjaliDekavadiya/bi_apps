# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ProjectQualityTeam(models.Model):
    
    _name = 'project.quality.team'
    _description = "Project Quality Team"
    _rec_name = 'name'


    name = fields.Char(
        string= 'Name',
        required= True
    )
    member_ids = fields.Many2many(
        'res.users',
        string='Team Members',
        required= True
    )
    team_manager_id = fields.Many2one(
        'res.users',
        string='Team Manager',
        required= True
    )
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:       
