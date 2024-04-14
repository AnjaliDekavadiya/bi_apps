# -*- coding: utf-8 -*-

#from openerp import models, fields, api, _
from odoo import models, fields, api, _


class Partner(models.Model):
    _inherit = "res.partner"

    #@api.multi
    @api.depends('wallet_ids')
    def _compute_wallet_balance(self):
        for rec in self:
            customer_wallet_ids = self.env['customer.wallet'].search([('customer_id', '=', rec.id)])
            credit_amount = 0.0
            debit_amount = 0.0
            for customer_wallet in customer_wallet_ids:
                if customer_wallet.balance_type == 'credit':
                    credit_amount += customer_wallet.amount
                if customer_wallet.balance_type == 'debit':
                    debit_amount += customer_wallet.amount
            rec.wallet_balance = credit_amount - debit_amount

    wallet_balance = fields.Float(
        string='Wallet Balance',
        compute='_compute_wallet_balance',
        #store=True,
    )
    wallet_ids = fields.One2many(
        'customer.wallet',
        'customer_id',
        string='Customer Wallet',
        readonly=True,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
