# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID

class RepairOrder(models.Model):
    _inherit = 'repair.order'

    probc_task_id = fields.Many2one(
        'project.task',
        string="Repair Task",
        copy=False
    )
    cloth_request_id = fields.Many2one(
        'cloth.request.details',
        string="Cloth Request",
        copy=False
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: