# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################
#
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class purchase_order(models.Model):
    _inherit = 'purchase.order'
    
    apply_discount = fields.Boolean('Apply Discount')
    discount_account_id = fields.Many2one('account.account','Discount Account', domain="[('is_discount','=',True)]")
    discount_type = fields.Selection([('fixed','Fixed'),('percent','Percent')],string='Discount Type')
    purchase_discount = fields.Float('Purchase Discount')
    
    @api.depends('order_line.price_total','apply_discount','purchase_discount','discount_type')
    def _amount_all(self):
        for order in self.sudo():
            amount_untaxed = amount_tax = disc_amt =  0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax

            if order.apply_discount:
                if order.discount_type == 'fixed':
                    disc_amt = order.purchase_discount
                else:
                    disc_amt = (order.purchase_discount * amount_untaxed) / 100
            
            order.update({
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax - disc_amt,
                'disc_amount': amount_untaxed  - disc_amt,
            })

    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all', tracking=True, compute_sudo=True)
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all', compute_sudo=True)
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all', compute_sudo=True)
    disc_amount = fields.Float('Amount After Discount',compute='_amount_all', compute_sudo=True)

    def button_confirm(self):
        for order in self:
            if order.apply_discount:
                if order.purchase_discount <= 0.0:
                    raise ValidationError(_('Purchase Discount Must be Greater then 0.'))
        return super(purchase_order,self).button_confirm()

    def get_bill_discount_line_vals(self):
        if self.discount_type == 'fixed':
            discount_amount = self.purchase_discount
        else:
            discount_amount = (self.amount_untaxed * self.purchase_discount) / 100
        if discount_amount > 0:
            discount_amount = discount_amount * -1
        return {
            'product_id': False,
            'name': 'Discount',
            'quantity': 1,
            'price_unit': discount_amount,
            'account_id':self.discount_account_id and self.discount_account_id.id or False,
            'sequence': 500000,
            'tax_ids':False,
        }

    def _prepare_invoice(self):
        res= super(purchase_order,self)._prepare_invoice()
        if self.apply_discount and self.discount_account_id:
            if 'invoice_line_ids' in res:
                val = self.get_bill_discount_line_vals()
                res.update({
                    'invoice_line_ids': [(0, 0, val)],
                })
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
