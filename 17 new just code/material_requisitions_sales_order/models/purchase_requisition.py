# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MaterialPurchaseRequisition(models.Model):
    _inherit = "material.purchase.requisition"

    so_maintenance_type = fields.Selection(
        selection=[
            ('manual', 'By Picking and Purchase'),
            ('somanual', 'By Sale Order')],
        string='Method',
        default='manual',
        ondelete={'manual': 'cascade'},
        copy=True,
        readonly=True,
    )

    custom_sale_order = fields.Many2one(
        'sale.order',
        string='Sale Order',
        copy=False,
    )

    is_sale_create = fields.Boolean(
        string="Sale Order Created",
        copy=False,
    )

    # @api.multi #odoo13
    def open_requisition_sale_order(self):
        '''
        Smart button in material purchase requisition.
        Click the button and get the all sale order record and sale order line.
        '''
        self.ensure_one()
        res = self.env.ref('sale.action_orders')
        res = res.sudo().read()[0]
        res['domain'] = str([('custom_purchase_requisition', '=', self.id)])
        return res

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super(MaterialPurchaseRequisition, self).fields_get(allfields=allfields, attributes=attributes)
        state_val = res.get('state')
        try:

            state_lst = []
            for selection_val in state_val.get("selection"):
                if list(selection_val)[0] == 'stock' and self._context.get('default_so_maintenance_type') == 'somanual':
                    state_lst.append(tuple(['stock', 'Sale Order Created']))
                else:
                    state_lst.append(selection_val)
            res['state']['selection'] = state_lst
        except:
            pass
        return res

    # @api.multi #odoo13
    def requisition_confirm(self):
        if self.so_maintenance_type == "manual":
            requisition_line_pi_po = self.requisition_line_ids.filtered(lambda line: line.requisition_type == 'saleorder')
            if requisition_line_pi_po:
                raise ValidationError('You can not select sale order option.')

        elif self.so_maintenance_type == "somanual":
            requisition_line_sale_order = self.requisition_line_ids.filtered(lambda line: line.requisition_type != 'saleorder')
            if requisition_line_sale_order:
                raise ValidationError(' By Sale Order can not create a Picking and Purchase line')

        return super(MaterialPurchaseRequisition, self).requisition_confirm()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
