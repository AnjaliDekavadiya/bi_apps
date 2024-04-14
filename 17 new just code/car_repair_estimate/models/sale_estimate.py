# -*- coding: utf-8 -*-

from odoo import models, fields, _


class SaleEstimate(models.Model):
    _inherit = 'sale.estimate'

    custom_car_repair_id = fields.Many2one(
        'car.repair.support',
        string='Car Repair Request',
        readonly=True,
        copy=False
    )