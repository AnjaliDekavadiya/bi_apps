# -*- coding: utf-8 -*

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    laundry_task_id = fields.Many2one(
        'project.task',
        string="Task",
        readonly=True,
        copy=False,
    )
    laundry_request_id = fields.Many2one(
        'laundry.business.service.custom',
        string='Laundry Request',
        readonly=True,
        copy=False,
    )