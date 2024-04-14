# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    custom_purchase_requisition = fields.Many2one(
        'material.purchase.requisition',
        string='Purchase Requisition',
        copy=False,
    )


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    custom_purchase_requisition_line = fields.Many2one(
        'material.purchase.requisition.line',
        string='Purchase Requisition',
        Copy=False,
    )
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
