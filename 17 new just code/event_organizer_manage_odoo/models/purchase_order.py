# -*- coding: utf-8 -*-

from odoo import fields, models, api

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    event_custom_id = fields.Many2one(
        'event.event',
        string='Event',
        copy=False
    )

    # @api.model
    # def create(self, vals):
    #     if vals.get('custom_requisition_id') and 'custom_requisition_id' in vals:
    #         custom_requisition_id = self.env['material.purchase.requisition'].browse(vals.get('custom_requisition_id'))
    #         vals.update({'event_custom_id':custom_requisition_id.event_custom_id.id})
    #     return super(PurchaseOrder, self).create(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('custom_requisition_id') and 'custom_requisition_id' in vals:
                custom_requisition_id = self.env['material.purchase.requisition'].browse(vals.get('custom_requisition_id'))
                vals.update({'event_custom_id':custom_requisition_id.event_custom_id.id})
        return super(PurchaseOrder, self).create(vals_list)

    def _prepare_invoice(self):
        result = super(PurchaseOrder, self)._prepare_invoice()
        result.update({'event_custom_id':self.event_custom_id.id})
        return result