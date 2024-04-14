# -*- coding: utf-8 -*-

from odoo import models, fields


class CarRepairSupport(models.Model):
    _inherit = 'car.repair.support'

    nature_of_service_ids = fields.Many2many(
        'car.service.nature',
        string="Nature of Services"
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
