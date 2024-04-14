# -*- coding: utf-8 -*-

from odoo import models, fields

class ProjectTask(models.Model):
    _inherit = "project.task"
    
    custom_fleet_id = fields.Many2one(
        'fleet.request',
        string='Fleet Repair',
        readonly=True,
        copy=False,
    )
  
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

