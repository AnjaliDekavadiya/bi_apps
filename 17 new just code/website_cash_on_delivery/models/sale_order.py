# coding: utf-8

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # @api.multi #odoo13
    @api.depends('order_line','partner_id',
                 'partner_id.country_id',
                 'partner_id.state_id',
                 'partner_id.zip'
                 )
    def _check_cash_on_deliver(self):
#        cod = self.env['payment.acquirer'].search([('provider', '=', 'cod')])
        cod = self.env['payment.provider'].search([('code', '=', 'cod')])
        zip_name = []
        for zipcode in cod.cod_zip_code_ids:
            zip_name.append(zipcode.name)
        for rec in self:
            rec.is_cod = True
            if rec.is_cod:
                # check for country
                if cod.available_country_ids:
                    if not rec.partner_id.country_id:
                        rec.is_cod = False
                    elif rec.partner_id.country_id.id not in cod.available_country_ids.ids:
                        rec.is_cod = False
            if rec.is_cod:
                # check for state
                if cod.cod_state_ids:
                    if not rec.partner_id.state_id:
                        rec.is_cod = False
                    elif rec.partner_id.state_id.id not in cod.cod_state_ids.ids:
                        rec.is_cod = False
            if rec.is_cod:
                # check for zip
                if zip_name:
                    if not rec.partner_id.zip:
                        rec.is_cod = False
                    elif rec.partner_id.zip not in zip_name:
                        rec.is_cod = False
            if rec.is_cod:
                # check for product
                if any(l.product_id.not_allow_cod for l in rec.order_line):
                    rec.is_cod = False
            if rec.is_cod:
                # check for amount
                # amount_total  = rec.currency_id.compute(rec.amount_total, rec.company_id.currency_id)
                amount_total = rec.currency_id._convert(
                        abs(rec.amount_total),
                        rec.currency_id,
                        rec.company_id,
                        rec.date_order,
                    )
                if amount_total < cod.cod_min_order_amount or amount_total > cod.cod_max_order_amount:
                    rec.is_cod = False
            if rec.is_cod:
                if not rec.partner_id.cod_payment_acquire_id:
                    rec.is_cod = False
#           
#                     
#                     for line in rec.order_line:
#                         if line.product_id.not_allow_cod and amount_total >= cod.min_order_amount and amount_total <= cod.max_order_amount and rec.partner_id.country_id.id in cod.country_ids.ids and rec.partner_id.state_id.id in cod.state_ids.ids and (rec.partner_id.zip in zip_name or not rec.partner_id.zip) or not cod.zip_code_ids.ids:
#                             rec.is_cod = True
#         else:
#             for rec in self:
#                 amount_total  = rec.currency_id.compute(rec.amount_total, rec.company_id.currency_id)
#                 for line in rec.order_line:
#                     if line.product_id.not_allow_cod and amount_total >= cod.min_order_amount and amount_total <= cod.max_order_amount:
#                         rec.is_cod = True

    is_cod = fields.Boolean(
        string='Valid for Cash On Delivery?',
        default=False,
        store=True,
        compute='_check_cash_on_deliver',
    )

    # @api.multi #odoo13
    def show_collection(self):
        self.ensure_one()
        # res = self.env.ref('website_cash_on_delivery.action_cash_on_delivery')
        # res = res.sudo().read()[0]
        res = self.env['ir.actions.act_window']._for_xml_id('website_cash_on_delivery.action_cash_on_delivery')
        res['domain'] = str([('saleorder_id', '=', self.id)])
        res['context'] = {'default_saleorder_id': self.id}
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
