# -*- coding: utf-8 -*-

#from openerp import models, fields, api
from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    wallet_used = fields.Float(
        'Wallet Amount Used',
    )
    wallet_transaction_id = fields.Many2one(
        'customer.wallet',
        string='Wallet Transaction',
    )

    #@api.multi
    def action_done(self):
        res = super(SaleOrder, self).action_done()
        for rec in self:
            wallet_product = self.env['product.template'].sudo().search([('is_wallet_product', '=', True)])
            for line in rec.order_line:
                if line.product_id.product_tmpl_id.is_wallet_product:
#                     amount = rec.currency_id.compute(rec.amount_total, rec.company_id.currency_id)
#                    amount = rec.currency_id._convert(rec.amount_total, rec.company_id.currency_id, rec.company_id, rec.confirmation_date or fields.Date.today())
                    amount = rec.currency_id._convert(rec.amount_total, rec.company_id.currency_id, rec.company_id, rec.date_order or fields.Date.today())
                    vals ={
                        'customer_id': rec.partner_id.id,
                        'amount': amount,
                        'currency_id': rec.currency_id.id,
                        'company_id': rec.company_id.id,
                        'balance_type': 'credit',
                        'sale_order_id': rec.id,
                        'reference': 'sale_order',
                        'sale_order_id': rec.id,
                        'state': 'done',
                    }
                    self.env['customer.wallet'].sudo().create(vals)
        return res

    #@api.multi
    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        for rec in self:
#            if rec.transaction_ids and rec.transaction_ids[0].acquirer_id.provider == 'wallet':
            if rec.transaction_ids and rec.transaction_ids[0].provider_id.code == 'wallet':
                note = 'Refund' + ' ' + rec.name + ' ' + 'sales order amount.'
                vals = {
                        'customer_id': rec.partner_id.id,
                        'date': fields.Datetime.now(),
                        'amount': rec.amount_total,
                        'currency_id': rec.currency_id.id,
                        'company_id': rec.company_id.id,
                        'balance_type': 'credit',
                        'sale_order_id': rec.id,
                        'note': note,
                    }
                self.env['customer.wallet'].sudo().create(vals)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
