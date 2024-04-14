# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    event_custom_id = fields.Many2one(
        'event.event',
        string='Event',
        copy=False,
    )

    # @api.model
    # def create(self, vals):
    #     if vals.get('custom_requisition_id'):
    #         custom_requisition_id = self.env['material.purchase.requisition'].browse(vals.get('custom_requisition_id'))
    #         vals.update({'event_custom_id':custom_requisition_id.event_custom_id.id})
    #     return super(StockPicking, self).create(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('custom_requisition_id'):
                custom_requisition_id = self.env['material.purchase.requisition'].browse(vals.get('custom_requisition_id'))
                vals.update({'event_custom_id':custom_requisition_id.event_custom_id.id})
        return super(StockPicking, self).create(vals_list)