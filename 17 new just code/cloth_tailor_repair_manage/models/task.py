# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID

class ProjectTask(models.Model):
    _inherit = 'project.task'

    probc_repair_id = fields.Many2one(
        'repair.order',
        string="Repair Order",
        copy=False
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: