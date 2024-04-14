# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    custom_company_currency_id = fields.Many2one('res.currency', string="Company Currency", 
        related='company_id.currency_id', 
        readonly=True, 
        store=True,
    )
    custom_amount_tax_signed = fields.Monetary(
        string='Tax', currency_field='custom_company_currency_id',
        store=True, readonly=True, compute='_compute_amount',
    )
    custom_amount_total_company_signed = fields.Monetary(string='Total', currency_field='custom_company_currency_id',
        store=True, readonly=True, compute='_compute_amount',
    )
    custom_amount_untaxed_signed = fields.Monetary(string='Untaxed Amount', currency_field='custom_company_currency_id',
        store=True, readonly=True, compute='_compute_amount')

    # custom_amount_margin_signed = fields.Monetary(string='Margin Company Currency', currency_field='custom_company_currency_id',
    #     store=True, readonly=True, 
    #     compute='_compute_amount'
    #     )

    # @api.one #odoo13
    # @api.depends('amount_total', 'amount_untaxed')
    # def _compute_amount(self):
    #     amount_total_company_signed = self.amount_total
    #     amount_untaxed_signed = self.amount_untaxed
    #     if self.currency_id and self.currency_id != self.company_id.currency_id:
    #         amount_total_company_signed = self.currency_id.compute(self.amount_total, self.company_id.currency_id)
    #         amount_untaxed_signed = self.currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
    #     self.amount_total_company_signed = amount_total_company_signed
    #     self.amount_untaxed_signed = amount_untaxed_signed
    #     self.amount_tax_signed = (
    #         self.amount_total_company_signed - self.amount_untaxed_signed)

    @api.depends('amount_total', 'amount_untaxed')
    def _compute_amount(self):
        for rec in self:
            custom_amount_total_company_signed = rec.amount_total
            custom_amount_untaxed_signed = rec.amount_untaxed
            if rec.currency_id and rec.currency_id != rec.company_id.currency_id:
                custom_amount_total_company_signed = rec.currency_id._convert(rec.amount_total, rec.company_id.currency_id, 
                   rec.order_line.order_id.company_id , rec.date_order)
                custom_amount_untaxed_signed = rec.currency_id._convert(rec.amount_untaxed, rec.company_id.currency_id,
                    rec.order_line.order_id.company_id , rec.date_order)
            rec.custom_amount_total_company_signed = custom_amount_total_company_signed
            rec.custom_amount_untaxed_signed = custom_amount_untaxed_signed
            rec.custom_amount_tax_signed = (
                rec.custom_amount_total_company_signed - rec.custom_amount_untaxed_signed)
