# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    custom_cloth_request_ids = fields.Many2many(
        'cloth.request.details',
        string="Cloth Requests"
    )

    # def _create_invoices(self, grouped=False, final=False): #odoo13
    def _create_invoices(self, grouped=False, final=False, date=None): #odoo14
        res = super(SaleOrder, self)._create_invoices(grouped, final)
        for rec in self:
            if rec.custom_cloth_request_ids:
                res.write({
                    'custom_cloth_request_ids': [(6, 0, rec.custom_cloth_request_ids.ids)]
                })
        return res