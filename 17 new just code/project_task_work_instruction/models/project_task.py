# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. 
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class Task(models.Model):
    _inherit = 'project.task'

    custom_work_instruction = fields.Binary(
        string="worksheet",
    )

class Project(models.Model):
    _inherit = 'project.project'

    custom_project_planning = fields.Binary(
        string="Planning",
    )
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
