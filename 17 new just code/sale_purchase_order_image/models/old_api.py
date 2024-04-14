# -*- coding: utf-8 -*-
# from openerp import fields, models, api
from odoo import fields, models, api


class sale_order_line(models.Model):
    _inherit='sale.order.line'
    
    # @api.one
    # @api.depends('order_id')
    # def _get_line_numbers(self):
    #     line_num = 0
    #     for rec in self:
    #         for line_rec in rec.order_id.order_line:
    #             line_num += 1
    #             line_rec.line_no = line_num

    @api.depends('order_id')
    def _get_line_numbers(self):
        line_num = 0
        for rec in self:
            line_num += 1
            rec.line_no = line_num

    line_no = fields.Integer(
        compute='_get_line_numbers',
        string='No.',
        store=True,
    )
    
    
class purchase_order_line(models.Model):
    _inherit='purchase.order.line'
    
    # @api.one
    # @api.depends('order_id')
    # def _get_line_numbers(self):
    #     line_num = 0
    #     for line_rec in self.order_id.order_line:
    #         line_num += 1
    #         line_rec.line_no = line_num

    @api.depends('order_id')
    def _get_line_numbers(self):
        line_num = 0
        for rec in self:
            line_num += 1
            rec.line_no = line_num

    line_no = fields.Integer(
        compute='_get_line_numbers',
        string='No.',
        store=True,
    )
