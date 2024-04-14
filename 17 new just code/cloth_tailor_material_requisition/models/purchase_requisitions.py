# -*- coding: utf-8 -*-

from odoo import models, fields , api


class MaterialPurchaseRequisition(models.Model):
    _inherit = "material.purchase.requisition"

    custom_cloth_request_id = fields.Many2one(
        'cloth.request.details',
        string='Cloth Request',
        readonly=False,
        copy=False,
    )
    custom_workorder_request_id = fields.Many2one(
        'project.task',
        string='Workorder Request',
        readonly=False,
        copy=False,
    )

class MaterialPurchaseRequisitionLine(models.Model):
    _inherit = "material.purchase.requisition.line"

    custom_line_id = fields.Many2one(
        'material.requisition.cloth.req',
        string='Cloth Requisition Line',
        readonly=False,
        copy=False,
    )

    @api.model
    def create(self, values):
        res = super(MaterialPurchaseRequisitionLine, self).create(values)
        if 'custom_line_id' in values:
            custom_line_id = self.env['material.requisition.cloth.req'].browse(values.get('custom_line_id'))
            custom_line_id.write({
                'requisition_line_id': res.id
                })
        return res
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
