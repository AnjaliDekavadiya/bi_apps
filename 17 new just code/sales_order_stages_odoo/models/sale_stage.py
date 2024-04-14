# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

class CustomSaleOrderStage(models.Model):
    _name = 'custom.sale.order.stage'
    _description = 'Sale Order Stages'

    name = fields.Char(
        string='Name',
        required=True,
    )
    sequence = fields.Integer(
        string='Sequence',
    )
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: