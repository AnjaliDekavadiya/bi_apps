# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class MaterialPurchaseRequisitionLine(models.Model):
    _inherit = "material.purchase.requisition.line"

    requisition_type = fields.Selection(selection_add=
        [('saleorder', 'Sale Order')],
        ondelete={'saleorder': 'cascade'},
        
    )
    custom_sale_order_line = fields.Many2one(
        'sale.order.line',
        string='Sale Order',
        copy=False,
    )
    is_sale_create_line = fields.Boolean(
        string="Sale Order Created",
        copy=False,
    )

    @api.model
    def default_get(self, fields):
        res = super(MaterialPurchaseRequisitionLine, self).default_get(fields)
        if self._context.get('default_so_maintenance_type') == 'somanual':
            if res.get('requisition_type'):
                res['requisition_type']='saleorder'
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
