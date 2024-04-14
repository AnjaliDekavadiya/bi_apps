# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. 
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class RecurringTask(models.Model):
    _name = 'recurring.task'
    _description = 'Recurring Task'
    _rec_name = 'task_id'
    
    task_recurring = fields.Selection(
        [('daily','Daily'),
         ('weekly','Weekly'),
         ('monthly','Monthly'),
         ('yearly','Yearly')],
        string='Recurring Period',
        required=True,
    )
    task_id = fields.Many2one(
        'project.task',
        string='Task Template',
        copy=False,
        required=True
    )
    active = fields.Boolean(
        string="Active",
        default=True
    )
    code = fields.Char(
        string="Code",
        required=True
    )
    name = fields.Char(
        string="Name",
        required=True
    )
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:   