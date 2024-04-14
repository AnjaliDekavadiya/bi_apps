# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    custom_number_quote = fields.Char(
        string='Quotation Number',
        readonly= True,
        copy=False,
    )

    # @api.model
    # def create(self, vals):
    #     vals['name'] = self.env['ir.sequence'].next_by_code('custom.sale.quotation')
    #     return super(SaleOrder,self).create(vals)


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('custom.sale.quotation')
        return super(SaleOrder,self).create(vals_list)


    def action_confirm(self):
        for order in self:
            seq_date = None
            if order.date_order:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(order.date_order))
            if order.company_id.id:
                # company_x = order.company_id.id
                order.write({
                    # 'name': self.env['ir.sequence'].with_context(force_company=order.company_id.id).next_by_code(
                    #     'sale.order', sequence_date=seq_date) or _('New'), #17/03/2021
                    'name': self.env['ir.sequence'].with_context(company_id=order.company_id.id).with_company(order.company_id).next_by_code(
                        'sale.order', sequence_date=seq_date) or _('New'), #17/03/2021
                    'custom_number_quote' : self.name
                })
            else:
                order.write({
                    'name': self.env['ir.sequence'].next_by_code('sale.order', sequence_date=seq_date) or _('New'),
                    'custom_number_quote' : self.name
                    })
        return super(SaleOrder, self).action_confirm()